import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from afeplc_data_scraper import manual_pull 
import time

st.write(st.secrets)

SHEET_NAME = st.secrets["sheet_name"]
CREDS_PATH = st.secrets["creds_path"]
GCP_CREDENTIALS = st.secrets["gcp_service_account"]


st.set_page_config(layout="wide")

# === Load data from Google Sheets ===
@st.cache_data(ttl=300)  
def load_data(SHEET_NAME, worksheet_name):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).worksheet(worksheet_name)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        # Ensure 'Value' is numeric, change the name of
        df["Utilization %"] = pd.to_numeric(df["Value"], errors="coerce")
        df.dropna(subset=["Serialization", "Utilization %"], inplace=True)
        return True, df
    except Exception as e:
        return False, f"Error loading {worksheet_name}: {e}"

# === Sidebar Refresh Buttons ===
inducts = ["Induct 101","Induct 102","Induct 103","Induct 104","Induct 105", "Induct 106", "Induct 107", "Induct 108"]
timeframes = ["Min", "Hour", "Day"]

st.sidebar.header("📥 Manual Refresh Options")

# Toggle button for value marker annotations
text_markers = None
toggle_markers= st.sidebar.toggle("Display Values", value=True, key='B1', help="Turn **on/off** utilization % value markers for a neater display", disabled=False, label_visibility="visible")
if toggle_markers:         
    text_markers = "Utilization %"
    markers = True

for induct in inducts:
    st.sidebar.markdown(f"**{induct}**")
    for timeframe in timeframes:
        if st.sidebar.button(f"Refresh {timeframe} Data - {induct}"):
            with st.spinner(f"Pulling {induct} {timeframe} data..."):
                success, msg = manual_pull(induct, timeframe)
                if success:
                    st.success(msg)
                    time.sleep(2.5)
                    st.cache_data.clear()
                    st.rerun()
                    
                else:
                    st.error(msg)

def fetch_data_safe(worksheet_name):
    success, result = load_data(SHEET_NAME, worksheet_name)
    if success:
        return result
    else:
        st.warning(result)
        return pd.DataFrame()
    
# === Main Dashboard layout ===
st.title(":wrench: AFE Induct Data Monitor :rocket:")

induct_101_min_data = fetch_data_safe("Induct 101 Min")
induct_101_hour_data = fetch_data_safe("Induct 101 Hour")
induct_101_day_data = fetch_data_safe("Induct 101 Day")

induct_102_min_data = fetch_data_safe("Induct 102 Min")
induct_102_hour_data = fetch_data_safe("Induct 102 Hour")
induct_102_day_data = fetch_data_safe("Induct 102 Day")

induct_103_min_data = fetch_data_safe("Induct 103 Min")
induct_103_hour_data = fetch_data_safe("Induct 103 Hour")
induct_103_day_data = fetch_data_safe("Induct 103 Day")

induct_104_min_data = fetch_data_safe("Induct 104 Min")
induct_104_hour_data = fetch_data_safe("Induct 104 Hour")
induct_104_day_data = fetch_data_safe("Induct 104 Day")

induct_105_min_data = fetch_data_safe("Induct 105 Min")
induct_105_hour_data = fetch_data_safe("Induct 105 Hour")
induct_105_day_data = fetch_data_safe("Induct 105 Day")

induct_106_min_data = fetch_data_safe("Induct 106 Min")
induct_106_hour_data = fetch_data_safe("Induct 106 Hour")
induct_106_day_data = fetch_data_safe("Induct 106 Day")

induct_107_min_data = fetch_data_safe("Induct 107 Min")
induct_107_hour_data = fetch_data_safe("Induct 107 Hour")
induct_107_day_data = fetch_data_safe("Induct 107 Day")

induct_108_min_data = fetch_data_safe("Induct 108 Min")
induct_108_hour_data = fetch_data_safe("Induct 108 Hour")
induct_108_day_data = fetch_data_safe("Induct 108 Day")

# Make sure all the tabs span the width of the page and arent squashed
st.markdown("""
    <style>
    div[data-baseweb="tab-list"] {
        flex-wrap: wrap; /* Allows wrapping if too many tabs */
        justify-content: space-evenly; /* Evenly spread across width */
    }
    </style>
""", unsafe_allow_html=True)

tabs_1, tabs_2, tabs_3, tabs_4, tabs_5, tabs_6, tabs_7, tabs_8 = st.tabs(['Induct 101','Induct 102','Induct 103','Induct 104','Induct 105','Induct 106', 'Induct 107', 'Induct 108'])

# === Formatting the formatting ===
custom_colors_categorical = {'Combi_util': 'hotpink', 'Tote_util': 'orange', 'Tray_util': 'lightblue'}

# === Create Induct 101 ===
with tabs_1:
    st.subheader("📊 Induct 101")
# === Plot Graphs ===
    # Manually pull Specific induct monitoring data.

    fig_1 = px.line(induct_101_min_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers= toggle_markers, text= text_markers, title="Induct 101 Minute analysis")
    fig_1.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        ))
    
    st.plotly_chart(fig_1, use_container_width=True, key='A1' )

    fig_2 = px.line(induct_101_hour_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text= text_markers, title="Induct 101 Hourly analysis")
    fig_2.update_layout(
        legend=dict(
            orientation="h",  
            y=-0.2,  
            x=0.5, 
            xanchor="center"  
        )
    )
    st.plotly_chart(fig_2, use_container_width=True, key='A2')

    fig_3 = px.line(induct_101_day_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 101 Daily analysis")
    fig_3.update_layout(
        legend=dict(
            orientation="h", 
            y=-0.2,  
            x=0.5,  
            xanchor="center" 
        )
    )
    st.plotly_chart(fig_3, use_container_width=True, key='A3')

# === Create Induct 102 ===
with tabs_2:
    st.subheader("📊 Induct 102")
# === Plot Graphs ===
    # Manually pull Specific induct monitoring data.

    fig_1 = px.line(induct_102_min_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers= toggle_markers, text= text_markers, title="Induct 102 Minute analysis")
    fig_1.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        ))
    
    st.plotly_chart(fig_1, use_container_width=True, key='A4' )

    fig_2 = px.line(induct_102_hour_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text= text_markers, title="Induct 102 Hourly analysis")
    fig_2.update_layout(
        legend=dict(
            orientation="h",  
            y=-0.2,  
            x=0.5, 
            xanchor="center"  
        )
    )
    st.plotly_chart(fig_2, use_container_width=True, key='A5')

    fig_3 = px.line(induct_102_day_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 102 Daily analysis")
    fig_3.update_layout(
        legend=dict(
            orientation="h", 
            y=-0.2,  
            x=0.5,  
            xanchor="center" 
        )
    )
    st.plotly_chart(fig_3, use_container_width=True, key='A6')

# === Create Induct 103 ===
with tabs_3:
    st.subheader("📊 Induct 103")
# === Plot Graphs ===
    # Manually pull Specific induct monitoring data.

    fig_1 = px.line(induct_103_min_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers= toggle_markers, text= text_markers, title="Induct 103 Minute analysis")
    fig_1.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        ))
    
    st.plotly_chart(fig_1, use_container_width=True, key='A7' )

    fig_2 = px.line(induct_103_hour_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text= text_markers, title="Induct 103 Hourly analysis")
    fig_2.update_layout(
        legend=dict(
            orientation="h",  
            y=-0.2,  
            x=0.5, 
            xanchor="center"  
        )
    )
    st.plotly_chart(fig_2, use_container_width=True, key='A8')

    fig_3 = px.line(induct_103_day_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 103 Daily analysis")
    fig_3.update_layout(
        legend=dict(
            orientation="h", 
            y=-0.2,  
            x=0.5,  
            xanchor="center" 
        )
    )
    st.plotly_chart(fig_3, use_container_width=True, key='A9')

# === Create Induct 104 ===
with tabs_4:
    st.subheader("📊 Induct 104")
# === Plot Graphs ===
    # Manually pull Specific induct monitoring data.

    fig_1 = px.line(induct_104_min_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers= toggle_markers, text= text_markers, title="Induct 104 Minute analysis")
    fig_1.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        ))
    
    st.plotly_chart(fig_1, use_container_width=True, key='A10' )

    fig_2 = px.line(induct_104_hour_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text= text_markers, title="Induct 104 Hourly analysis")
    fig_2.update_layout(
        legend=dict(
            orientation="h",  
            y=-0.2,  
            x=0.5, 
            xanchor="center"  
        )
    )
    st.plotly_chart(fig_2, use_container_width=True, key='A11')

    fig_3 = px.line(induct_104_day_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 104 Daily analysis")
    fig_3.update_layout(
        legend=dict(
            orientation="h", 
            y=-0.2,  
            x=0.5,  
            xanchor="center" 
        )
    )
    st.plotly_chart(fig_3, use_container_width=True, key='A12')
# === Create Induct 105 ===
with tabs_5:
    st.subheader("📊 Induct 105")
# === Plot Graphs ===
    # Manually pull Specific induct monitoring data.

    fig_1 = px.line(induct_105_min_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers= toggle_markers, text= text_markers, title="Induct 105 Minute analysis")
    fig_1.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        ))
    
    st.plotly_chart(fig_1, use_container_width=True, key='A13' )

    fig_2 = px.line(induct_105_hour_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text= text_markers, title="Induct 105 Hourly analysis")
    fig_2.update_layout(
        legend=dict(
            orientation="h",  
            y=-0.2,  
            x=0.5, 
            xanchor="center"  
        )
    )
    st.plotly_chart(fig_2, use_container_width=True, key='A14')

    fig_3 = px.line(induct_105_day_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 105 Daily analysis")
    fig_3.update_layout(
        legend=dict(
            orientation="h", 
            y=-0.2,  
            x=0.5,  
            xanchor="center" 
        )
    )
    st.plotly_chart(fig_3, use_container_width=True, key='A15')

# === Create Induct 106 ===
with tabs_6:
    st.subheader("📊 Induct 106")
    fig_1 = px.line(induct_106_min_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 106 Minute analysis")
    fig_1.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center            
        )

    )

    st.plotly_chart(fig_1, use_container_width=True, key='1' )

    fig_2 = px.line(induct_106_hour_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 106 Hourly analysis")
    fig_2.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        )
    )
    st.plotly_chart(fig_2, use_container_width=True, key= '2')

    fig_3 = px.line(induct_106_day_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 106 Daily analysis")
    fig_3.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        )
    )
    st.plotly_chart(fig_3, use_container_width=True, key='3')

    # === Create Induct 107 ===
with tabs_7:
    st.subheader("📊 Induct 107")
    fig_1 = px.line(induct_107_min_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 107 Minute analysis")
    fig_1.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center            
        )

    )

    st.plotly_chart(fig_1, use_container_width=True, key='4' )

    fig_2 = px.line(induct_107_hour_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 107 Hourly analysis")
    fig_2.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        )
    )
    st.plotly_chart(fig_2, use_container_width=True, key= '5')

    fig_3 = px.line(induct_107_day_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 107 Daily analysis")
    fig_3.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        )
    )
    st.plotly_chart(fig_3, use_container_width=True, key='6')

# === Create Induct 108 ===
with tabs_8:
    st.subheader("📊 Induct 108")
    fig_1 = px.line(induct_108_min_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 108 Minute analysis")
    fig_1.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center            
        )

    )

    st.plotly_chart(fig_1, use_container_width=True, key='7' )

    fig_2 = px.line(induct_108_hour_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 108 Hourly analysis")
    fig_2.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        )
    )
    st.plotly_chart(fig_2, use_container_width=True, key= '8')

    fig_3 = px.line(induct_108_day_data, x="Serialization", y="Utilization %", color="Category", color_discrete_map=custom_colors_categorical, markers=toggle_markers, text=text_markers, title="Induct 108 Daily analysis")
    fig_3.update_layout(
        legend=dict(
            orientation="h",  # Horizontal legend
            y=-0.2,  # Move legend below the graph
            x=0.5,  # Center the legend horizontally
            xanchor="center"  # Align legend to center
        )
    )
    st.plotly_chart(fig_3, use_container_width=True, key='9')
