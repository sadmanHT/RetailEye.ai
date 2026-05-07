import os
import time
import requests
import pandas as pd
import streamlit as st

# --- Configuration ---
st.set_page_config(page_title="RetailEye AI Dashboard", layout="wide")
API_URL = "http://localhost:8000"

def main():
    st.title("RetailEye AI Dashboard")
    st.markdown("Welcome to the RetailEye AI store intelligence system. Upload a CCTV footage video to process person tracking, queue detection, and zone heatmaps automatically.")

    # --- Sidebar ---
    st.sidebar.header("Configuration")
    
    uploaded_file = st.sidebar.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])
    model_path = st.sidebar.text_input("Model Weights Path", value="models/weights/best.pt")
    show_live = st.sidebar.checkbox("Show Live Preview", value=False)
    
    run_btn = st.sidebar.button("Run Analysis", type="primary")

    # --- State Management ---
    if "job_id" not in st.session_state:
        st.session_state.job_id = None
    if "results" not in st.session_state:
        st.session_state.results = None
    if "video_path" not in st.session_state:
        st.session_state.video_path = None

    # --- Action: Run Analysis ---
    if run_btn:
        if not uploaded_file:
            st.error("Please upload a video file first.")
        else:
            # 1. Trigger processing
            try:
                # We send 'video' as a file and 'model_path' as form data
                files = {"video": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"model_path": model_path}
                
                with st.spinner("Uploading and starting job..."):
                    resp = requests.post(f"{API_URL}/analyze/video", files=files, data=data)
                    resp.raise_for_status()
                    st.session_state.job_id = resp.json()["job_id"]
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend API: {e}")
                return

    # --- Polling Status ---
    if st.session_state.job_id and not st.session_state.results:
        job_id = st.session_state.job_id
        
        with st.spinner("Processing video... This may take a while depending on file size."):
            while True:
                try:
                    status_resp = requests.get(f"{API_URL}/job/status/{job_id}")
                    if status_resp.status_code == 200:
                        status_data = status_resp.json()
                        status = status_data["status"]
                        
                        if status == "completed":
                            st.session_state.video_path = status_data.get("result_path")
                            break
                        elif status == "failed":
                            st.error(f"Job failed: {status_data.get('error')}")
                            st.session_state.job_id = None
                            break
                            
                    time.sleep(2)
                except requests.exceptions.RequestException as e:
                    st.error(f"Error querying job status: {e}")
                    st.session_state.job_id = None
                    break

        # Fetch results immediately upon success
        if st.session_state.video_path:
            with st.spinner("Fetching analytics report..."):
                try:
                    analytics_resp = requests.get(f"{API_URL}/analytics/{job_id}")
                    if analytics_resp.status_code == 200:
                        st.session_state.results = analytics_resp.json()
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to fetch analytics: {e}")

    # --- Render Results ---
    if st.session_state.results:
        st.success("Analysis Complete!")
        st.markdown("---")
        
        res = st.session_state.results
        
        # Extract aggregate metrics
        total_people = res.get("unique_people_tracked", 0)
        video_duration = res.get("video_duration_seconds", 0)
        zone_summaries = res.get("zone_summaries", {})
        
        # Calculate hottest zone and average 
        busiest_zone = "N/A"
        max_visits = -1
        total_dwell = 0.0
        total_zone_visits_overall = 0
        
        for z, zdata in zone_summaries.items():
            visits = zdata.get("total_visits", 0)
            avg_dwell = zdata.get("average_dwell_seconds", 0.0)
            if visits > max_visits:
                max_visits = visits
                busiest_zone = z
            total_dwell += avg_dwell * visits
            total_zone_visits_overall += visits
            
        overall_avg_dwell = (total_dwell / total_zone_visits_overall) if total_zone_visits_overall > 0 else 0.0

        # 1. Executive Summary Metrics
        st.header("Executive Summary")
        st.write("Top level insights regarding video throughput and global movement metrics.")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total People Tracked", total_people)
        col2.metric("Video Duration (sec)", f"{video_duration:.1f}")
        col3.metric("Busiest Zone", busiest_zone)
        col4.metric("Avg Dwell Time (sec)", f"{overall_avg_dwell:.1f}")
        
        st.markdown("---")
        
        # 2. Zone Occupancy Bar Chart
        st.header("Zone Occupancy")
        st.write("Total unique visits registered inside each monitored polygon boundary.")
        
        chart_data = {"Zone": [], "Visits": []}
        for z, zdata in zone_summaries.items():
            chart_data["Zone"].append(z)
            chart_data["Visits"].append(zdata.get("total_visits", 0))
            
        if chart_data["Zone"]:
            df_chart = pd.DataFrame(chart_data)
            st.bar_chart(df_chart.set_index("Zone"))
        else:
            st.info("No zone data available to graph.")

        st.markdown("---")
        
        # 3. Exact Dwell Times Pivot Table
        st.header("Individual Dwell Times")
        st.write("Detailed interaction times in seconds per uniquely tracked customer identity mapped to specific zones.")
        
        dwell_dict = res.get("dwell_times", {})
        table_data = []
        for tid, zones in dwell_dict.items():
            row = {"Track ID": tid}
            for z, seconds in zones.items():
                if seconds > 0:
                    row[z] = f"{seconds:.1f}"
            table_data.append(row)
            
        if table_data:
            df_table = pd.DataFrame(table_data).fillna("-")
            st.dataframe(df_table, use_container_width=True)
        else:
            st.info("No dwell times formally recorded yet.")

        st.markdown("---")

        # 4. Final Annotated Output Video
        st.header("Annotated Video Footage")
        st.write("Playback of the processed footage containing YOLO bounds, tracking identities, mapped polygon zones, and Gaussian heatmaps combined.")
        
        video_file = st.session_state.video_path
        if video_file and os.path.exists(video_file):
            try:
                # Load the bytes from local store (Since the API writes its output here)
                with open(video_file, "rb") as vf:
                    video_bytes = vf.read()
                st.video(video_bytes)
            except Exception as e:
                st.error(f"Failed to read result video stream: {e}")
        else:
            st.warning("Video file could not be loaded from local disk. Ensure output paths match between the API and dashboard environments.")

if __name__ == "__main__":
    main()