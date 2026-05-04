import requests

API_URL = "http://localhost:8000"

def get_chat_response(question: str, role: str) -> str:
    """Sends the user's question and role to the FastAPI backend."""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"question": question, "role": role}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("answer", "Error: No answer received.")
    except Exception as e:
        return f"Error: {e}"