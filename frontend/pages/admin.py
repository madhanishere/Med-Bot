import streamlit as st
import requests

st.set_page_config(page_title="Knowledge Base Admin", page_icon="⚙️")


st.markdown("""
    <style>
    /* ... (keep your existing button and file uploader styles here) ... */

    /* NEW: Hide the 'Press Enter to submit form' overlapping text */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    .login-box {
        border: 3px solid black;
        padding: 20px;
        border-radius: 0px;
        box-shadow: 6px 6px 0px black;
        background-color: white;
    }
            div[data-baseweb="textarea"] > div {
        border: 3px solid black !important;
        border-radius: 0px !important;
        background-color: #f8f9fa !important;
        box-shadow: 4px 4px 0px black !important;
    }
            div[data-baseweb="textarea"] > div {
        border: 3px solid black !important;
        border-radius: 0px !important;
        background-color: #f8f9fa !important;
        box-shadow: 4px 4px 0px black !important;
    }
    
    /* NEW: Force the text inside to be black */
    div[data-baseweb="textarea"] textarea {
        color: black !important;
    }
    div[data-baseweb="textarea"] textarea {
        color: black !important;
        caret-color: black !important; 
    }
    /* NEW: Make the placeholder text dark gray so it's visible */
    div[data-baseweb="textarea"] textarea::placeholder {
        color: #555555 !important;
    }
            div[data-baseweb="textarea"] textarea:disabled {
        color: black !important;
        -webkit-text-fill-color: black !important;
        opacity: 1 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ Admin Panel")


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:
    st.markdown("### Please log in to access the dashboard.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In")
        
        if submit_button:
            try:

                response = requests.post(
                    "http://localhost:8000/login",
                    json={"username": username, "password": password}
                )
                
                if response.status_code == 200:
                    st.session_state.logged_in = True
                    st.rerun() 
                else:
                    st.error("❌ Invalid username or password.")
            except Exception as e:
                st.error(f"Cannot connect to server. Is FastAPI running? Error: {e}")


else:

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown("Upload new `.txt` or `.pdf` documents to update the hospital's knowledge base. The AI will automatically read and learn the new information.")


    uploaded_file = st.file_uploader("Select a document", type=["txt", "pdf"])

    if st.button("Upload and Train AI"):
        if uploaded_file is not None:
            with st.spinner("Uploading and retraining database... This may take a moment."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post("http://localhost:8000/upload", files=files)
                    response.raise_for_status()
                    st.success(response.json()["message"])
                except Exception as e:
                    st.error(f"Error updating knowledge base: {e}")
        else:
            st.warning("Please select a file to upload first.")


    st.markdown("---")

    st.subheader("⚡ Quick Content Update")
    st.markdown("Directly type new hospital rules, visiting hours, or FAQs here.")
    
    with st.form("quick_update_form", clear_on_submit=True):
        new_content = st.text_area("New Knowledge Base Content", height=150)
        

        submit_update = st.form_submit_button("Add to Knowledge Base")
        
        if submit_update:
            if new_content.strip():
                with st.spinner("Learning new information..."):
                    try:
                        response = requests.post(
                            "http://localhost:8000/update-faq",
                            json={"content": new_content}
                        )
                        response.raise_for_status()
                        st.success(response.json()["message"])
                    except Exception as e:
                        st.error(f"Error saving content: {e}")
            else:
                st.warning("Please enter some text before submitting.")
    st.subheader("Chat Logs")
    st.markdown("Review recent questions asked by visitors.")

    if st.button("Refresh Logs"):
        try:
            response = requests.get("http://localhost:8000/logs")
            response.raise_for_status()
            logs = response.json().get("logs", "")
            st.text_area("Conversation History", value=logs, height=300, disabled=True)
        except Exception as e:
            st.error(f"Could not fetch logs: {e}")