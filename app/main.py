import streamlit as st
import os
import json
import folium
from streamlit_folium import st_folium

from app.utils import check_password, get_tools_config
from app.extractor import run_all_extractions
from app.analyzer import get_initial_strategy, synthesize_findings
from app.tools import execute_tool

# Ensure uploads dir exists
os.makedirs("uploads", exist_ok=True)

st.set_page_config(page_title="OSINT Agent", layout="wide")

if not check_password():
    st.stop()

st.title("🕵️ OSINT Agent")
st.markdown("Upload an image and/or provide context to start the automated investigation.")

# --- Initialization ---
with st.spinner("Initializing tool definitions..."):
    get_tools_config()

# --- Input Section ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload Image (optional)", type=["jpg", "jpeg", "png"])
with col2:
    user_context = st.text_area("Context / Target (Name, URL, email, etc.)", height=100)

if st.button("Start Investigation", type="primary"):
    if not uploaded_file and not user_context:
        st.warning("Please provide an image or some context to begin.")
        st.stop()

    image_path = None
    if uploaded_file:
        image_path = os.path.join("uploads", uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # --- Phase 1: Extraction ---
    st.header("1. Raw Extracted Data")
    with st.spinner("Extracting metadata..."):
        extracted_data = run_all_extractions(image_path) if image_path else {}
        st.json(extracted_data)

    # --- Phase 2: AI Strategy ---
    st.header("2. AI Analysis & Strategy")
    with st.spinner("Consulting Gemini..."):
        strategy = get_initial_strategy(image_path, extracted_data, user_context)
        
        if "error" in strategy:
            st.error(strategy["error"])
            st.stop()

        col_f, col_c = st.columns([3, 1])
        with col_f:
            st.subheader("Findings")
            for f in strategy.get("findings", []):
                 st.write(f"- {f}")
        with col_c:
             st.metric("Confidence", strategy.get("confidence", "Unknown").upper())

    # --- Phase 3: Tool Execution ---
    st.header("3. Automated Tool Results")
    tool_results = {}
    tools_to_run = strategy.get("tools_to_run", [])
    
    if not tools_to_run:
        st.info("No automated tools identified for this phase.")
    
    for tool_cmd in tools_to_run:
        tool_name = tool_cmd.get("tool_name", "Unknown")
        reason = tool_cmd.get("reason", "")
        with st.expander(f"🛠️ Executing: {tool_name}"):
             st.caption(f"Reason: {reason}")
             with st.spinner("Running..."):
                 res = execute_tool(tool_cmd)
                 tool_results[tool_name] = res
                 st.json(res)

    # --- Phase 4: Map (If GPS found) ---
    gps_data = extracted_data.get("gps", {})
    if gps_data.get("latitude") and gps_data.get("longitude"):
         st.header("4. Geolocation")
         lat = gps_data["latitude"]
         lon = gps_data["longitude"]
         
         # Basic DD conversion if necessary (pyexiftool sometimes returns strings or deg/min/sec)
         # Assuming float for simplicity in this MVP
         try:
             lat = float(lat)
             lon = float(lon)
             m = folium.Map(location=[lat, lon], zoom_start=13)
             folium.Marker([lat, lon]).add_to(m)
             st_folium(m, width=700, height=400)
         except Exception as e:
             st.error(f"Could not render map with provided coordinates: {e}")

    # --- Phase 5: Final Synthesis ---
    st.header("5. Next Steps & Synthesis")
    with st.spinner("Synthesizing final report..."):
        final_report = synthesize_findings(user_context, extracted_data, tool_results)
        st.markdown(final_report)

    # --- Export ---
    st.divider()
    full_report = {
        "context": user_context,
        "extracted_data": extracted_data,
        "ai_strategy": strategy,
        "tool_results": tool_results,
        "final_synthesis": final_report
    }
    
    st.download_button(
        label="Download Full Report (JSON)",
        data=json.dumps(full_report, indent=2),
        file_name="osint_report.json",
        mime="application/json"
    )
