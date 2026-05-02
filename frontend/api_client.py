import requests
import streamlit as st


API_URL = "http://localhost:8000"

def get_chat_response(question: str) -> str:
    """Sends the user's question to the FastAPI backend and returns the answer."""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"question": question}
        )
        response.raise_for_status() 
        data = response.json()
        return data.get("answer", "Error: No answer received from server.")
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the backend API. Is your FastAPI server running?"
    except Exception as e:
        return f"An unexpected error occurred: {e}"