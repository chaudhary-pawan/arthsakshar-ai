import streamlit as st
import openpyxl
import requests
import time
import os

# Configuration
API_URL = "http://localhost:8000/api/campaigns/start"
EXCEL_FILE = "call_responses.xlsx"

st.set_page_config(page_title="ArthSakshar AI", page_icon="📞", layout="wide")

st.title("📞 ArthSakshar AI – Voice Calling Campaign Manager")
st.markdown("Ensure your FastAPI backend is running before clicking Start Campaign.")

st.sidebar.header("Campaign Controls")

# Start Campaign Button
if st.sidebar.button("🚀 Start Campaign", type="primary"):
    try:
        response = requests.post(API_URL, json={"name": "Dashboard Campaign"})
        if response.status_code == 200:
            st.sidebar.success("✅ Campaign Started Successfully!")
        else:
            st.sidebar.error(f"⚠️ Failed to start: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.sidebar.error("❌ Cannot connect to FastAPI server. Is uvicorn running on port 8000?")

st.sidebar.markdown("---")
st.sidebar.subheader("Live Tracking")

auto_refresh = st.sidebar.checkbox("Auto-refresh data (Every 5s)", value=True)

# Main display area for Excel Data
st.subheader("📊 Live Call Responses")
data_container = st.empty()

def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
            ws = wb.active
            data = []
            for row in ws.iter_rows(values_only=True):
                data.append(row)
            if not data:
                return []
            
            # First row is header
            headers = data[0]
            # Convert to list of dicts for Streamlit dataframe
            return [dict(zip(headers, row)) for row in data[1:]]
        except Exception as e:
            return [{"Error": f"Could not read excel: {e}"}]
    else:
        return [{"Message": "call_responses.xlsx does not exist yet. Please create it or run a campaign."}]

def render_html_table(data_list):
    if not data_list:
        return "<p>No entries found.</p>"
        
    # Check for error messages returned as list of dicts
    if len(data_list) == 1 and ("Error" in data_list[0] or "Message" in data_list[0]):
        msg = list(data_list[0].values())[0]
        return f"<div style='padding: 1rem; border-radius: 5px; background-color: #3b2a2a; color: #ff8c8c; border: 1px solid #ff4d4d;'>{msg}</div>"
        
    headers = list(data_list[0].keys())
    
    html = "<table style='width: 100%; text-align: left; border-collapse: collapse; margin-top: 1rem; color: #e0e0e0; font-family: sans-serif;'>"
    html += "<thead><tr>"
    for h in headers:
        html += f"<th style='border-bottom: 2px solid #555; padding: 10px; background-color: #262730;'>{h}</th>"
    html += "</tr></thead><tbody>"
    
    for row in data_list:
        html += "<tr style='background-color: #0e1117;'>"
        for h in headers:
            val = row.get(h, "")
            # Ensure None translates to empty string
            if val is None: val = ""
            html += f"<td style='border-bottom: 1px solid #333; padding: 10px;'>{val}</td>"
        html += "</tr>"
        
    html += "</tbody></table>"
    return html

# Auto-refresh loop
if auto_refresh:
    data_list = load_data()
    data_container.markdown(render_html_table(data_list), unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📝 Live Execution Logs")
    if os.path.exists("arthsakshar.log"):
        with open("arthsakshar.log", "r") as f:
            lines = f.readlines()
            # Show last 20 lines
            log_text = "".join(lines[-20:])
            st.code(log_text, language="log")
    else:
        st.info("No logs generated yet. Click Start Campaign to begin.")
        
    time.sleep(5)
    st.rerun()
else:
    data_list = load_data()
    data_container.markdown(render_html_table(data_list), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📝 Live Execution Logs")
    if os.path.exists("arthsakshar.log"):
        with open("arthsakshar.log", "r") as f:
            lines = f.readlines()
            log_text = "".join(lines[-20:])
            st.code(log_text, language="log")
    else:
        st.info("No logs generated yet. Click Start Campaign to begin.")

    if st.button("🔄 Manual Refresh"):
        st.rerun()
