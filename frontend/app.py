import streamlit as st
from api_client import get_chat_response

st.set_page_config(page_title="Hospital FAQ Bot", page_icon="🏥", layout="centered")

# --- NEW: Pop-up Modal for Role Selection ---
@st.dialog("Welcome to the Hospital FAQ Bot")
def role_selection_modal():
    st.markdown("### Who are you today?")
    st.write("Please select your role so I can tailor my assistance to you:")
    
    # Create a nice 2x2 grid of buttons for the roles
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Visitor", use_container_width=True):
            st.session_state.current_role = "Visitor"
            st.session_state.messages = [{"role": "assistant", "content": "Hello! I am ready to assist you as a Visitor. How can I help?"}]
            st.rerun()
            
        if st.button("Doctor", use_container_width=True):
            st.session_state.current_role = "Doctor"
            st.session_state.messages = [{"role": "assistant", "content": "Hello! I am ready to assist you as a Doctor. How can I help?"}]
            st.rerun()
            
    with col2:
        if st.button("Patient", use_container_width=True):
            st.session_state.current_role = "Patient"
            st.session_state.messages = [{"role": "assistant", "content": "Hello! I am ready to assist you as a Patient. How can I help?"}]
            st.rerun()
            
        if st.button("Admin", use_container_width=True):
            st.session_state.current_role = "Admin"
            st.session_state.messages = [{"role": "assistant", "content": "Hello! I am ready to assist you as an Admin. How can I help?"}]
            st.rerun()

# --- Intercept the user if they haven't picked a role ---
if "current_role" not in st.session_state:
    role_selection_modal()
    st.stop() # This hides the rest of the chat UI until they make a choice!

# --- Sidebar ---
st.sidebar.title("User Profile")
st.sidebar.markdown(f"**Current Role:** `{st.session_state.current_role}`")

# Give them a way to trigger the pop-up again if they made a mistake
if st.sidebar.button("Change Role"):
    del st.session_state.current_role
    st.rerun()



# --- Main UI ---
st.title("🏥 Hospital Assistant")
st.markdown(f"**Chatting as:** `{st.session_state.current_role}`")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_chat_response(prompt, st.session_state.current_role)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})