#THE GOAL IS TO ACHIEVE A REUSABLE FUNCTION
# THE ALL IN ONE SCRAPER FRFR
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import APIError
import logging


SHEET_NAME = st.secrets["sheet_name"]
CREDS_PATH = st.secrets["creds_path"]
AFE_INDUCT_PORTALS = dict(st.secrets["afe_portals"])
AFEINDUCT_SCRAPE_CONFIGS = [dict(config) for config in st.secrets["afe_configs"]]
USERNAME = st.secrets["username"]
PASSWORD = st.secrets["password"]

# Configure logging once globally at start of your main script or module
logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename='scrape_log.txt',
    filemode='a',
    encoding='utf-8',
    level=logging.DEBUG
)

# Cache structure
sheet_cache = {}

pd.set_option("display.max_colwidth", None)

# === Extract Functions ===
def extract_info_day(serialization):
    match = re.search(
        r"s_30_Day_Result\[(\d+)\]\.(Combi_util|tote_util|tray_util)", serialization
    )
    if match:
        return int(match.group(1)), match.group(2)
    return None, None

def extract_info_hour(serialization):
    match = re.search(
        r"s_24_Hourly_result\[(\d+)\]\.(Combi_util|tote_util|tray_util)", serialization
    )
    if match:
        return int(match.group(1)), match.group(2)
    return None, None

def extract_info_min(serialization):
    match = re.search(
        r"s_60_minute_result\[(\d+)\]\.(Combi_util|tote_util|tray_util)", serialization
    )
    if match:
        return int(match.group(1)), match.group(2)
    return None, None

EXTRACTORS = {
    "Min": extract_info_min,
    "Hour": extract_info_hour,
    "Day": extract_info_day,
}

for config in AFEINDUCT_SCRAPE_CONFIGS:
    config["extract_func"] = EXTRACTORS[config["timeframe"]]

def auth_gspread(CREDS_PATH, SHEET_NAME, worksheet_name):
    global sheet_cache

    if SHEET_NAME in sheet_cache:
        spreadsheet = sheet_cache[SHEET_NAME]
    else:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
        client = gspread.authorize(creds)
        try:
            spreadsheet = client.open(SHEET_NAME)
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = client.create(SHEET_NAME)
        try:
            plc_sheet = spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            plc_sheet = spreadsheet.add_worksheet(title=worksheet_name, rows="100", cols="10")
        return plc_sheet
    
# --- Retry logic to handle Google API 429 errors ---
def retry_api_call(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except APIError as e:
            if "429" in str(e):
                wait = (2 ** attempt) + 1
                logging.warning(f"Rate limit hit. Retrying in {wait:.1f}s...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")


def manual_pull(induct,timeframe):
    worksheet_name = f"{induct} {timeframe}"
    portal_url = AFE_INDUCT_PORTALS[induct]
    scrape_config = next(
        c for c in AFEINDUCT_SCRAPE_CONFIGS if c["induct"] == induct and c["timeframe"] == timeframe
    )
    data_url = scrape_config["url"]
    extract_func = scrape_config["extract_func"]

    try:
        logging.info(f"Starting scrape for {worksheet_name}...")
        
        # Set up Selenium options
        options = Options()
        # Running locally so ignore any security warnings from HTTP connection
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--headless")  
        driver = webdriver.Chrome(options=options)  # Allowing selenium driver to do automations
        driver.get(portal_url)  # While TRUE use selenium to open page
        time.sleep(3)  # Prevent rate-clicking block due to multiple requests (300s cooldown)
        logging.info("Navigated to PLC portal.")

       # Authenticate page
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "intro_enter")))  
            logging.info("Authentication complete.") 
            driver.find_element(By.CLASS_NAME, "intro_enter").click() 
        except Exception: 
            logging.info("No authentication element found; continuing.")  

       # Login to PLC
        driver.find_element(By.NAME, "Login").clear()  # Begin logging into PLC
        driver.find_element(By.NAME, "Login").send_keys(USERNAME) 
        driver.find_element(By.NAME, "Password").clear()  #
        driver.find_element(By.NAME, "Password").send_keys(PASSWORD) 
        driver.find_element(By.CLASS_NAME, "Login_Button").click()
        time.sleep(3)

        # Navigate to Table
        driver.get(data_url)  # 106 Hour Watch Table
        table = driver.find_element(By.CSS_SELECTOR, ".Vartable.s7webtable") 
        rows = table.find_elements(By.TAG_NAME, "tr")
        data_raw = [[col.text for col in row.find_elements(By.TAG_NAME, "td")] for row in rows]

        # Transform Data into DataFrame
        df = pd.DataFrame(data_raw)
        data = df.copy()
        data.columns = ["Serialization", "Address", "Format", "Value", "Comment"]
        data_2 = data.copy()
        data_2 = data_2[["Serialization", "Value"]]
        data_2 = data_2.iloc[1:, :]
        data_2 = data_2.iloc[:-1, :]


        # Extract information using extract_func
        data_2[["Count", "Utility"]] = data_2["Serialization"].apply(
            lambda x: pd.Series(extract_func(x)))

        # Sort the DataFrame based on Count and Utility order
        utility_order = {"Combi_util": 1, "tote_util": 2, "tray_util": 3}
        data_2["Utility_Order"] = data_2["Utility"].map(utility_order)

        data_2 = data_2.sort_values(by=["Count", "Utility_Order"]).drop(columns=["Utility_Order"])

        # Format the output
        data_2["Formatted"] = data_2.apply(lambda row: f"{row['Utility']}", axis=1)
        new_data  = data_2[['Formatted','Value']].reset_index(drop=True)

        # Fix missing utility rows
        expected_pattern = ['Combi_util', 'tote_util', 'tray_util']
        corrected_data = []
        pattern_index = 0

        for _, row in new_data.iterrows():
            current_label = row['Formatted']

            while current_label != expected_pattern[pattern_index]:
                corrected_data.append({'Formatted': expected_pattern[pattern_index], 'Value': 0})
                pattern_index = (pattern_index + 1) % len(expected_pattern)
            
            corrected_data.append({'Formatted': current_label, 'Value': row['Value']})
            pattern_index = (pattern_index + 1) % len(expected_pattern)

        # Create a corrected DataFrame
        corrected_df = pd.DataFrame(corrected_data)
        new_data = corrected_df.copy()

        df = pd.DataFrame(new_data['Value'].values.reshape(-1, 3), columns=['Combi_util', 'Tote_util', 'Tray_util'])
        # Reset index so it becomes a column
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Serialization"}, inplace=True)

        # Melt dataframe to long format for Plotly Express
        df_melted = df.melt(id_vars=["Serialization"],value_vars=['Combi_util', 'Tote_util', 'Tray_util'], var_name="Category", value_name="Value")
        df_melted["Value"] = df_melted["Value"].astype(int) # make sure all the numbers in the value column are int types
        df_melted['Value'] = df_melted[['Value']].map(lambda x: 105 if x < 0 or x > 100 else x)

        # Upload to GSheet
        plc_sheet = auth_gspread(CREDS_PATH, SHEET_NAME, worksheet_name)
        plc_sheet.clear()
        plc_sheet.update([df_melted.columns.values.tolist()] + df_melted.astype(str).values.tolist())

        logging.info(f"Scrape and upload for {worksheet_name} completed successfully.")
        print(f"Scrape and upload for {worksheet_name} completed successfully.")
        return True, f"✅ Data pulled and uploaded for {worksheet_name}"
            
    
    except Exception as e:
        logging.exception("Error occurred during scrape:")
        return False, f"❌ Error during {worksheet_name}: {e}"
    finally:
        try:
            driver.quit()
        except:
            pass
