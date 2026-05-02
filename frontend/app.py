import streamlit as st
from api_client import get_chat_response


st.set_page_config(
    page_title="Med-Bot",
    layout="centered"
)

st.title("Med-Bot :")
st.markdown("Welcome !")



if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



if prompt := st.chat_input("Ask a question... (e.g., Where is the Cardiology department?)"):
    

    with st.chat_message("user"):
        st.markdown(prompt)
    

    st.session_state.messages.append({"role": "user", "content": prompt})
    

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_chat_response(prompt)
            st.markdown(response)
            

    st.session_state.messages.append({"role": "assistant", "content": response})