## TELEGRAM BOT WITH FLASK

import os
from telegram import *
import babayan_actions as misha
from flask import Flask

print("Bot started")

app = Flask(__name__)


def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    print('Chat id', chat_id)
    print('Message', text)
    return chat_id, text


@app.route('/',  methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        print(msg)

    return "Hello world"

if __name__ == '__main__':
    app.run(debug=True)