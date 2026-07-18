import streamlit as st
import requests

st.title("Upload Candidate Resume and JD")

API_URL = st.session_state.get("API_URL", "http://localhost:8000/api/v1")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume (PDF)")
    resume_file = st.file_uploader("Choose a PDF Resume", type=["pdf"])

with col2:
    st.subheader("2. Upload Job Description")
    jd_file = st.file_uploader("Choose a JD file (TXT or PDF)", type=["txt", "pdf"])

if st.button("Analyze Candidate"):
    if not resume_file or not jd_file:
        st.error("Please upload both a resume and a job description.")
    else:
        with st.spinner("Uploading and analyzing..."):
            # Upload Resume
            resume_res = requests.post(
                f"{API_URL}/upload", 
                files={"file": (resume_file.name, resume_file, "application/pdf")}
            )
            
            # Upload JD
            jd_res = requests.post(
                f"{API_URL}/upload_jd", 
                files={"file": (jd_file.name, jd_file, "text/plain")}
            )
            
            if resume_res.status_code == 200 and jd_res.status_code == 200:
                resume_path = resume_res.json().get("path")
                jd_path = jd_res.json().get("path")
                
                # Analyze
                analyze_res = requests.post(
                    f"{API_URL}/analyze",
                    json={"resume_path": resume_path, "jd_path": jd_path}
                )
                
                if analyze_res.status_code == 200:
                    st.success("Analysis complete!")
                    st.json(analyze_res.json())
                else:
                    st.error(f"Analysis failed: {analyze_res.text}")
            else:
                st.error("Upload failed.")
