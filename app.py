import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from src.analytics_engine import WelfordStreamAnalyzer
from src.db_manager import IndustrialDBManager
from config.database_config import ANALYTICS_SETTINGS

st.set_page_config(page_title="Industrial Condition Monitoring", layout="wide")
st.title("🔥 Enterprise Real-Time Condition Monitoring")

# Initialize Session State
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = WelfordStreamAnalyzer(
        threshold=ANALYTICS_SETTINGS["z_threshold"],
        warmup=ANALYTICS_SETTINGS["warmup_samples"]
    )
if 'history_df' not in st.session_state:
    st.session_state.history_df = pd.DataFrame(columns=['Time', 'Temperature', 'Status'])
if 'last_time' not in st.session_state:
    st.session_state.last_time = None

db = IndustrialDBManager()
db.setup_database()

# UI Placeholders
status_placeholder = st.empty()
chart_placeholder = st.empty()

st.sidebar.markdown("### System Diagnostics")
st.sidebar.success("✅ Database Connection: Stable")
st.sidebar.info(f"Anomaly Threshold: {ANALYTICS_SETTINGS['z_threshold']} Sigma")

while True:
    record = db.fetch_latest_telemetry()
    
    if record:
        current_time, temp, equip_name = record
        
        if current_time != st.session_state.last_time:
            st.session_state.last_time = current_time
            temp = float(temp)
            
            # Real-time processing
            is_anomaly, z_val, current_mean = st.session_state.analyzer.process_sample(temp)
            
            status = 'Critical Anomaly' if is_anomaly else 'Nominal'
            
            new_row = {'Time': current_time.strftime("%H:%M:%S"), 'Temperature': temp, 'Status': status}
            st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame([new_row])]).tail(30)
            
            # Update Dashboard Metrics
            with status_placeholder.container():
                st.markdown(f"**Target Asset:** `{equip_name}`")
                cols = st.columns(3)
                cols[0].metric("Live Temperature", f"{temp} °C", delta=f"Z-Score: {z_val:.2f}", delta_color="inverse" if is_anomaly else "normal")
                cols[1].metric("Rolling Baseline (Mean)", f"{current_mean:.2f} °C")
                if is_anomaly:
                    cols[2].error("🚨 CRITICAL: Thermal Anomaly Detected!")
                else:
                    cols[2].success("✅ System Operating within Nominal Parameters.")

            # Render Plotly Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=st.session_state.history_df['Time'], y=st.session_state.history_df['Temperature'], 
                                     mode='lines+markers', name='Temperature', 
                                     marker=dict(color=['red' if s == 'Critical Anomaly' else '#00B4D8' for s in st.session_state.history_df['Status']], size=10)))
            
            fig.add_hline(y=current_mean, line_dash="dash", line_color="#00FF00", annotation_text="Baseline Target")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=30, b=0))
            
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            
    time.sleep(1)