import streamlit as st
import requests

st.title("Chat with Recruiter Agent")

API_URL = st.session_state.get("API_URL", "http://localhost:8000/api/v1")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about candidates..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            res = requests.post(
                f"{API_URL}/chat",
                json={"message": prompt, "session_id": "default_session"}
            )
            
            if res.status_code == 200:
                full_response = res.json().get("response", "Error getting response.")
            else:
                full_response = f"API Error: {res.text}"
                
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
