import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = "8005204216:AAGRaliYOC1VkGUwKBXgdJDpfnYHGuUEij0"
CHAT_ID = "1374000776"

def send_test_message():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": "✅ Nifty Trend Alert Bot Connected!"}
    requests.post(url, data=data)

@app.route("/")
def home():
    send_test_message()
    return "Bot Connected"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
