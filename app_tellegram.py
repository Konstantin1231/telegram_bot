## TELEGRAM BOT WITH FLASK

import os
from telegram import *
from babayan_actions import *
from flask import Flask, request, Response
from dotenv import load_dotenv
import requests


print("Bot started")

app = Flask(__name__)
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
print(BOT_TOKEN)

def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    print('Chat id', chat_id)
    print('Message', text)
    return chat_id, text

# to send a message
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    return response

@app.route('/',  methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        print(msg)
        chat_id, user_message = message_parser(msg)
        response = say_hi()
        print(response)
        send_message(chat_id, response)
        return Response(status=200)
    else:
        return "<h1>Hello world</h1>"


if __name__ == '__main__':
    app.run(host = "0.0.0.0" , debug=True, port=5000)