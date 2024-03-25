## TELEGRAM BOT WITH FLASK

import os
from telegram import *
from babayan_actions import *
from flask import Flask, request, Response
from dotenv import load_dotenv
import requests
import icecream as ic
import time

BABAYAN_ID = 1414008992

print("Bot started")

Black_List = {}

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
    return chat_id, text, user_name


def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    user_name = message['message']['from']['first_name']
    return chat_id, text, user_name


# to send a message
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": 'Markdown'}
    response = requests.post(url, json=payload)
    return response
def message_update(chat_id, text, msg_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {'chat_id': chat_id, 'message_id': msg_id, 'text': text, "parse_mode": 'Markdown'}
    response = requests.post(url, json=payload)
    return response

def send_stream_data(chat_id, user_message, msg_id):
    new_msg = " "
    i = 0
    for chunks in Ollama.stream(user_message):
        new_msg = new_msg + chunks
        if i%50==0:
            message_update(chat_id, new_msg, msg_id)
        i+=1
        message_update(chat_id, new_msg, msg_id)
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
    response = requests.post(url, json=payload)
    print(response)
    return response


# mute user
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
    print(response)  # For debugging


def ready_to_get_banned(user_id, max_limit=3):
    BAN = False
    key = str(user_id)
    Black_List[key] += 1
    if Black_List[key] >= max_limit:
        BAN = True
        Black_List[key] = 0
    return BAN


@app.route('/', methods=['POST', 'GET'])
def index():
    audio = False
    if request.method == 'POST':
        msg = request.get_json()
        try:
            user_id = msg['message']['from']['id']
            if not str(user_id) in Black_List:
                Black_List[str(user_id)] = 0
            if 'message' in msg and 'voice' in msg['message']:
                audio = True
                chat_id, user_message, user_name = handle_voice_message(msg['message'])
            else:
                chat_id, user_message, user_name = message_parser(msg)
        except BaseException:
            return Response(status=200)
        else:
            if misha_mentioned(user_message):
                suffix = ""
                small_dick_mentioned = is_small_dick(user_message)
                if small_dick_mentioned:
                    is_banned = ready_to_get_banned(user_id)
                    if is_banned:
                        ban_user_for_duration(chat_id, user_id, 60)
                        suffix = "You just banned me, because I said that your dick is small, fuck."
                        print(user_id, ": Banned")
                    else:

                        muted_time = Black_List[str(user_id)] * 60
                        mute_user_for_duration(chat_id, user_id, muted_time)
                        suffix = (f"You just muted me for {muted_time} seconds, because I said that your dick is "
                                  f"small, fuck.")
                        print(user_id, ": Muted for ", muted_time, " seconds")

                prefix = f" {user_name} say:"
                if user_id == BABAYAN_ID:
                    prefix = f" Babayan (Misha's good friend) say:"
                elif Black_List[str(user_id)] == 2:
                    prefix = f" {user_name} ( Has Karma count = 2 ) say:"
                input = prefix + " " + user_message + " " + suffix
                response = say(input=input)
                print(Black_List)
                if "say" in user_message or audio:
                    audio_file_path = text_to_audio(response)
                    send_audio_message(chat_id, audio_file_path)
                else:
                    send_message(chat_id, response)
            elif "/code" in user_message:
                response = send_message(chat_id, " ...")
                msg_id = response.json()["result"]["message_id"]
                response = Ollama.invoke(user_message)
                message_update(chat_id, response, msg_id)
                """response = send_message(chat_id, " ...")
                msg_id = response.json()["result"]["message_id"]
                send_stream_data(chat_id, user_message, msg_id)"""




        return Response(status=200)
    else:
        return "<h1>Hello</h1>"


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5000)
