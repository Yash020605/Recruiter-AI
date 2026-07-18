import streamlit as st
import requests
import pandas as pd
import json

st.title("Candidate Dashboard")

API_URL = st.session_state.get("API_URL", "http://localhost:8000/api/v1")

def load_candidates():
    try:
        res = requests.get(f"{API_URL}/candidates")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Failed to fetch candidates: {e}")
    return []

candidates = load_candidates()

if not candidates:
    st.info("No candidates found.")
else:
    # Prepare data for dataframe
    df_data = []
    for c in candidates:
        df_data.append({
            "ID": c.get("id"),
            "Name": c.get("name"),
            "Match Score": c.get("match_score", 0),
            "Email": c.get("email", ""),
            "Created At": c.get("created_at")
        })
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Candidate Details")
    selected_id = st.selectbox("Select Candidate ID to view details", options=df["ID"].tolist())
    
    if selected_id:
        selected_cand = next((c for c in candidates if c.get("id") == selected_id), None)
        if selected_cand:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {selected_cand.get('name')}")
                st.write(f"**Email:** {selected_cand.get('email')}")
                st.write(f"**Phone:** {selected_cand.get('phone')}")
                st.write(f"**Match Score:** {selected_cand.get('match_score')}%")
            
            with col2:
                st.write("**Recommendation:**")
                st.write(selected_cand.get("recommendation", "N/A"))
            
            st.write("**Matched Skills:**")
            try:
                ms = json.loads(selected_cand.get("matched_skills", "[]"))
                st.write(", ".join(ms) if ms else "None")
            except:
                st.write(selected_cand.get("matched_skills", "None"))
                
            st.write("**Missing Skills:**")
            try:
                mis = json.loads(selected_cand.get("missing_skills", "[]"))
                st.write(", ".join(mis) if mis else "None")
            except:
                st.write(selected_cand.get("missing_skills", "None"))
