import streamlit as st
import requests
import uuid

# Page configuration
st.set_page_config(
    page_title="SnapGPT",
    page_icon="⚡",
    layout="wide"
)

# API Configuration
API_URL = "https://snapgpt.labs.snaplogic.com/api/1/rest/slsched/feed/snaplogic/Bootcamp/AMER_November_2025/Agent_Jordan_api"
HEADERS = {
    "Authorization": "Bearer 12345",
    "Content-Type": "application/json"
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Header
st.title("⚡ SnapGPT")
st.markdown("*Powered by SnapLogic*")
st.divider()

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about your CRM data..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response with spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Transform chat history to API format
                api_messages = []
                for msg in st.session_state.messages:
                    api_messages.append({
                        "content": msg["content"],
                        "sl_role": "USER" if msg["role"] == "user" else "ASSISTANT"
                    })
                
                # Build payload with conversation history
                payload = {
                    "session_id": st.session_state.session_id,
                    "messages": api_messages
                }
                
                response = requests.post(
                    API_URL,
                    headers=HEADERS,
                    json=payload,
                    timeout=180
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract response from the API response format
                    if isinstance(data, list) and len(data) > 0:
                        assistant_response = data[0].get("response", "No response received.")
                    else:
                        assistant_response = "Unexpected response format."
                    
                    st.markdown(assistant_response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                else:
                    error_message = f"Error: API returned status code {response.status_code}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })
                    
            except requests.exceptions.Timeout:
                error_message = "Request timed out. Please try again."
                st.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })

# Sidebar with info and clear chat button
with st.sidebar:
    st.header("About SnapGPT")
    st.markdown("""
    SnapGPT is a chat interface that connects to your SnapLogic CRM data retriever.
    
    **Features:**
    - Natural language queries
    - CRM data analysis
    - Real-time responses
    - Conversational context
    
    **Example Questions:**
    - "Show me the top opportunities"
    - "What are the deals in negotiation?"
    - "List opportunities by stage"
    - "How about the closed deals?" (follow-up)
    """)
    
    st.divider()
    
    # Display session ID
    st.caption(f"Session ID: `{st.session_state.session_id[:8]}...`")
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    st.caption("Made with ⚡ by SnapLogic")
