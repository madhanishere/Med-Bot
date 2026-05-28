import requests

API_URL = "https://med-bot-vsmf.onrender.com"

def get_chat_response(question: str, role: str):

    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": question,
                "role": role
            }
        )

        response.raise_for_status()

        data = response.json()

        return data

    except Exception as e:
        return f"Error: {e}"