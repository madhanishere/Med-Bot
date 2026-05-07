import streamlit as st
from api_client import get_chat_response

st.set_page_config(page_title="Med-Bot", layout="centered")


chat_brutalism_css = """
<style>




    * { font-weight: 700 !important; }


    .stButton > button, 
    [data-testid="stFormSubmitButton"] button {
        background-color: #FFFFFF !important; 
        color: #000000 !important;
        border: 3px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000000 !important;
        transition: all 0.1s ease-in-out;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    

    .stButton > button:active, 
    [data-testid="stFormSubmitButton"] button:active {
        background-color: #000000 !important; 
        color: #FFFFFF !important;
        transform: translate(3px, 3px);
        box-shadow: 2px 2px 0px #000000 !important;
    }


    div[role="dialog"] {
        border: 4px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 10px 10px 0px #000000 !important;
        background-color: #FFFFFF !important;
    }


    [data-testid="stChatInput"] {
        border: 3px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 6px 6px 0px #000000 !important;
        background-color: #FFFFFF !important; 
    }
    

    [data-testid="stChatInput"] div[data-baseweb="textarea"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div {
        background-color: transparent !important;
        border: none !important;
    }


    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #000000 !important;
        font-weight: 700 !important;
        -webkit-text-fill-color: #000000 !important;
    }


    [data-testid="stChatInput"] button {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 2px 2px 0px #000000 !important;
        transition: all 0.1s ease-in-out;
    }
    

    [data-testid="stChatInput"] button:active {
        background-color: #000000 !important; 
        color: #FFFFFF !important;
        transform: translate(2px, 2px);
        box-shadow: 0px 0px 0px #000000 !important;
    }
    

    [data-testid="stChatInput"]:focus-within {
        border: 3px solid #000000 !important;
    }


    [data-testid="stChatMessageContent"] {
        
        
        
        
    }
</style>
"""

st.markdown(chat_brutalism_css, unsafe_allow_html=True)

@st.dialog("Welcome to Med-Bot")
def role_selection_modal():
    st.write("Please select your role so I can tailor my assistance to you:")
    
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

if "current_role" not in st.session_state:
    role_selection_modal()
    st.stop()

st.sidebar.title("User Role")
st.sidebar.markdown(f"**Current Role:** `{st.session_state.current_role}`")
if st.sidebar.button("Change Role"):
    del st.session_state.current_role
    st.rerun()

st.title("Med-Bot")
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