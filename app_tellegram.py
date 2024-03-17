## TELEGRAM BOT WITH FLASK

import os
from telegram import *
from babayan_actions import *
from flask import Flask, request, Response
from dotenv import load_dotenv
import requests
import icecream as ic
import time

print("Bot started")

app = Flask(__name__)
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def get_file_path(file_id):
    """Get the file path of the voice message."""
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}')
    file_path = response.json()['result']['file_path']
    return file_path

def download_audio(file_url):
    """Download the audio file from Telegram."""
    response = requests.get(file_url)
    # Assuming you want to save the file temporarily for processing
    temp_file_path = "audio_msg/temp_voice.mp3"
    with open(temp_file_path, 'wb') as audio_file:
        audio_file.write(response.content)
    return temp_file_path
def handle_voice_message(message):
    file_id = message['voice']['file_id']
    file_path = get_file_path(file_id)
    file_url = f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}'
    # Now, you would download the file and send it to a speech-to-text service
    # For example:
    audio_content = download_audio(file_url)
    text = convert_audio_to_text(audio_content)
    chat_id = message['chat']['id']
    user_name = message['from']['first_name']
    return  chat_id, text, user_name


def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    user_name = message['message']['from']['first_name']
    return chat_id, text, user_name

# to send a message
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    return response

# send audio message

def send_audio_message(chat_id, audio_file_path):
    """Send an audio message to a Telegram chat."""
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendAudio'
    files = {'audio': open(audio_file_path, 'rb')}
    data = {'chat_id': chat_id}
    response = requests.post(url, files=files, data=data)
    return response

# ban user

def ban_user_for_duration(chat_id, user_id, duration):
    """Temporarily bans a user from the chat."""
    until_date = int(time.time()) + duration  # Current time + duration in seconds
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/banChatMember'
    payload = {
        'chat_id': chat_id,
        'user_id': user_id,
        'until_date': until_date
    }
    print(user_id, ": Banned")
    response = requests.post(url, json=payload)
    return response

#mute user

from datetime import datetime, timedelta
import telegram

# Define permissions to revoke (mute) - Telegram Bot API version might affect available parameters
mute_permissions = telegram.ChatPermissions(
    can_send_messages=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False
)
def mute_user_for_duration(chat_id, user_id, duration):
    """Temporarily mutes a user in the chat."""
    until_date = int(time.time()) + duration
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/restrictChatMember'
    payload = {
        'chat_id': chat_id,
        'user_id': user_id,
        'permissions': mute_permissions.to_json(),  # Convert permissions to JSON string
        'until_date': until_date
    }
    response = requests.post(url, json=payload)
    print(response.text)  # For debugging


@app.route('/',  methods=['POST', 'GET'])
def index():
    audio = False
    if request.method == 'POST':
        msg = request.get_json()
        print(msg)
        try:
            if 'message' in msg and 'voice' in msg['message']:
                audio = True
                chat_id, user_message,  user_name = handle_voice_message(msg['message'])
                print(chat_id, user_message,  user_name)
            else:
                chat_id, user_message,  user_name = message_parser(msg)
        except BaseException:
            return Response(status=200)
        else:
            if misha_mentioned(user_message):
                is_banned = is_small_dick(user_message)
                print(is_banned)
                if is_banned:
                    user_id = msg['message']['from']['id']
                    mute_user_for_duration(chat_id, user_id, 60)
                    user_message = "You just muted me, because I said that your dick is small, fuck."
                input = f" {user_name}:" + " " + user_message
                response = say(input=input)
                if "say" in user_message or audio:
                    audio_file_path = text_to_audio(response)
                    send_audio_message(chat_id, audio_file_path)
                else:
                    send_message(chat_id, response)
        return Response(status=200)
    else:
        return "<h1>Hello</h1>"


if __name__ == '__main__':
    app.run(host = "0.0.0.0" , debug=False, port=5000)
