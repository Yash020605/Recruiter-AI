import streamlit as st
import pandas as pd
from frontend.api_client import api_client

import time

st.set_page_config(page_title="NEXUS AI Recruiter", page_icon="🚀", layout="wide")

# Inject Custom CSS for branding
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    h1 {
        color: #1E3A8A;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
</style>
""", unsafe_allow_html=True)

# Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "current_candidate_id" not in st.session_state:
    st.session_state.current_candidate_id = None

def login_view():
    st.title("AI Recruiter Assistant MVP")
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            res = api_client.login(username, password)
            if res.status_code == 200:
                token = res.json().get("access_token")
                st.session_state.access_token = token
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials. Try admin/admin for MVP fallback.")

def upload_view():
    st.title("Upload & Analyze")
    
    st.subheader("1. Upload Resumes (Batch)")
    uploaded_files = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Upload to System"):
            with st.spinner("Uploading batch..."):
                uploaded_ids = []
                for f in uploaded_files:
                    res = api_client.upload_resume(f.getvalue(), f.name)
                    if res.status_code == 201:
                        c_id = res.json().get("id")
                        uploaded_ids.append(c_id)
                    else:
                        st.error(f"Failed to upload {f.name}")
                if uploaded_ids:
                    st.session_state.current_candidate_ids = uploaded_ids
                    st.success(f"Successfully uploaded {len(uploaded_ids)} resumes!")
                    
    # Use current_candidate_ids or current_candidate_id for backwards compat
    c_ids = st.session_state.get("current_candidate_ids", [])
    if not c_ids and st.session_state.get("current_candidate_id"):
        c_ids = [st.session_state.current_candidate_id]
        
    if c_ids:
        st.subheader("2. Analyze against Job Description")
        jd = st.text_area("Paste Job Description here:", height=200)
        
        if st.button("Run LangGraph Analysis on Batch"):
            if not jd.strip():
                st.warning("Please provide a job description.")
            else:
                with st.spinner(f"Triggering Analysis for {len(c_ids)} candidates..."):
                    success_count = 0
                    for cid in c_ids:
                        res = api_client.trigger_analysis(cid, jd)
                        if res.status_code == 202:
                            success_count += 1
                        else:
                            st.error(f"Analysis failed for candidate {cid}: {res.text}")
                    if success_count > 0:
                        st.success(f"Analysis triggered successfully for {success_count} candidates! It is running in the background.")
                        st.info("Check the Candidate Dashboard for live results.")

def dashboard_view():
    st.title("Candidate Dashboard")
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("Refresh Data"):
            st.rerun()
    with col2:
        auto_refresh = st.checkbox("Auto-refresh every 5s")
        if auto_refresh:
            time.sleep(5)
            st.rerun()
        
    res = api_client.get_candidates()
    if res.status_code == 200:
        candidates = res.json()
        if not candidates:
            st.info("No candidates found in the database.")
            return
            
        # Display summary table
        df = pd.DataFrame(candidates)
        # Select key columns for the overview table
        display_cols = ["id", "name", "email", "match_score", "created_at"]
        existing_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[existing_cols], use_container_width=True)
        
        st.subheader("Detailed Reports")
        for c in candidates:
            with st.expander(f"Candidate {c.get('id')} - {c.get('name', 'Pending')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Score:** {c.get('match_score', 'N/A')}")
                    st.markdown(f"**Recommendation:** {c.get('recommendation', 'Pending')}")
                    st.markdown(f"**Matched Skills:** {c.get('matched_skills', 'Pending')}")
                with col2:
                    st.markdown(f"**Missing Skills:** {c.get('missing_skills', 'Pending')}")
                    st.markdown(f"**Extracted Skills:** {c.get('skills', 'Pending')}")
    else:
        st.error("Failed to fetch candidates.")

def chat_view():
    st.title("AI Agent Chat")
    st.info("Discuss candidate profiles with the intelligent recruiter assistant.")
    
    # Candidate Selection
    res = api_client.get_candidates()
    candidates = []
    if res.status_code == 200:
        candidates = res.json()
        
    if not candidates:
        st.warning("No candidates available to chat about. Please upload resumes first.")
        return
        
    # Create dropdown dictionary
    c_dict = {f"ID: {c['id']} - {c.get('name', 'Unknown')}": c['id'] for c in candidates}
    selected_name = st.selectbox("Select a Candidate to discuss", options=list(c_dict.keys()))
    selected_id = c_dict[selected_name]
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask a question about the candidate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chat_res = api_client.chat_with_agent(selected_id, prompt)
                if chat_res.status_code == 200:
                    reply = chat_res.json().get("reply", "No response.")
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                else:
                    st.error(f"Error: {chat_res.text}")

# Main Router
if not st.session_state.authenticated:
    login_view()
else:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload & Analyze", "Candidate Dashboard", "Agent Chat"])
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.access_token = None
        st.rerun()
        
    if page == "Upload & Analyze":
        upload_view()
    elif page == "Candidate Dashboard":
        dashboard_view()
    elif page == "Agent Chat":
        chat_view()
