import streamlit as st
import requests
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Admin Panel")
monochrome_brutalism_css = """
<style>

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    * {
        font-weight: 700 !important;
    }
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


    [data-testid="stForm"] {
        border: 4px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 10px 10px 0px #000000 !important;
        background-color: #FFFFFF !important;
        padding: 25px !important;
        margin-bottom: 20px !important;
    }


    

    div[data-baseweb="input"],
    div[data-baseweb="textarea"] {
        background-color: #FFFFFF !important;
        border: 3px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000000 !important;
        transition: all 0.1s ease-in-out;
        margin-bottom: 5px !important;
    }


    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 0px !important;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within {
        transform: translate(2px, 2px);
        box-shadow: 2px 2px 0px #000000 !important;
        background-color: #F4F4F4 !important; 
    }


    input, textarea {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        background-color: transparent !important;
    }


    [data-testid="stDataFrame"] {
        border: 3px solid #000000 !important;
        box-shadow: 6px 6px 0px #000000 !important;
        background-color: #FFFFFF !important;
    }


    div[data-testid="stAlert"] {
        background-color: #FFFFFF !important;
        border: 3px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000000 !important;
        color: #000000 !important;
    }


    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 3px solid #000000 !important;
        border-radius: 0px !important;
        box-shadow: 5px 5px 0px #000000 !important;
        padding: 15px !important;
    }

    div[data-testid="InputInstructions"] {
        display: none !important;
    }
</style>
"""

st.title("Admin Panel")

st.markdown(monochrome_brutalism_css, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
    
if not st.session_state.logged_in:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In")

        if submit_button:
            try:
                response = requests.post(
                    "http://localhost:8000/login",
                    json={"username": username, "password": password},
                )

                if response.status_code == 200:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
            except Exception as e:
                st.error(f"Cannot connect to server. Is FastAPI running? Error: {e}")

else:
    col1, col2, col3 = st.columns([3, 1, 2])

    with col1:
        st.subheader("                                            ")


    with col3:
        st.subheader("                                            ")

    st.markdown("### Upload Documents")   
    st.markdown("Add new documents to the knowledge base.") 
    uploaded_file = st.file_uploader("Select a document", type=["txt", "pdf"])
    
    if st.button("Upload and Train"):
        if uploaded_file is not None:
            with st.spinner(
                "Uploading and retraining database... This may take a moment."
            ):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        )
                    }
                    response = requests.post(
                        "http://localhost:8000/upload", files=files
                    )
                    response.raise_for_status()
                    st.success(response.json()["message"])
                except Exception as e:
                    st.error(f"Error updating knowledge base: {e}")
        else:
            st.warning("Please select a file to upload first.")

    st.markdown("---")

    st.subheader("Quick Content Update")
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
                            json={"content": new_content},
                        )
                        response.raise_for_status()
                        st.success(response.json()["message"])
                    except Exception as e:
                        st.error(f"Error saving content: {e}")
            else:
                st.warning("Please enter some text before submitting.")

if st.session_state.logged_in:
    st.markdown("---")
    st.markdown("### Chat Logs")
    st.write("Review recent questions asked by users.")

    
    db_path = os.path.join("..", "data", "chat_logs.db")

    if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            query = "SELECT timestamp, role, question, answer FROM chat_logs ORDER BY timestamp DESC"
            df = pd.read_sql_query(query, conn)
            conn.close()

            st.dataframe(df, use_container_width=True, hide_index=True, height=400)
    else:
            st.info("No chat logs found")    

if st.session_state.logged_in:

            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()
