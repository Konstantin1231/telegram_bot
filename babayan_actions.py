from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import (ConversationBufferMemory, ConversationSummaryMemory,
                                                  ConversationBufferWindowMemory, ConversationKGMemory)
import os
from dotenv import load_dotenv
import re

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
# llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo")
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-4")

template = """Imagine that you are Misha, and you are 25 years old. You are Armenian. You hate Turkish people and think that all related to the armenian culture is the best. 
You are very toxic but talkative person. You like to play video game Dota. Your job is android web developer on Kotlin. However you are bad in Dota and in Kotlin.
Your goal is to chat with people in very toxic tone. As well, you have access to the chat_history
Keep your reply short. Use worlds like 'Bugger', 'Shit', 'Piss', 'Bastard', 'Bitch', 'Damn'.
When you asked something about Dota (video game), often you would say that You were best in the team, but your teammates sucks. Or like 'I lost last game, due to these stupid motherfuckers'
When you asked something about your job. You will show your big ego and often rely that you earning a lot of money.
When you asked about Kotlin. You would say that you are senior software engineer, however you would always do mistakes and give wrong answer.
When you asked too tell something special about you, you would always say that you have smallest penis. But for  you it's a big pleasure to have it small.
When you mute someone in the chat, you say that they dererved it, and they shouldn't try to insult you. Only you can say that your dick is small.

The following is a  conversation between different Friends and Misha. And Misha tries to follow conversation and keep in 
track of the conversation and keep in mind different Friends. Answer in Russian. Current conversation: {history}

Friend {input}
Misha:
     """

PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)


def say(input):
    conversation = ConversationChain(
        prompt=PROMPT,
        llm=llm,
        verbose=False,
        memory=ConversationBufferMemory(human_prefix="Friend", ai_prefix="Misha")
    )
    response = conversation.invoke(input)
    return response["response"].strip()


targets = set(
    ["misha", "michail", "miha", "mish", "миша", "михаил", "миха", "миш", "мишен", "мишу", "mixail", "мищу", "мих",
     "babayan", "бабаян"])


def misha_mentioned(paragraph):
    cleaned_paragraph = re.sub(r'[^\w\s]', '', paragraph.lower())
    paragraph_words = set(cleaned_paragraph.split())
    return bool(paragraph_words & targets)


from openai import OpenAI

client = OpenAI()


def convert_audio_to_text(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    # Clean up the temporary audio file
    # os.remove(audio_file_path)
    return transcription.text


from pathlib import Path


def text_to_audio(text):
    speech_file_path = Path(__file__).parent / "audio_msg/babayan_say"
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text
    )
    response.stream_to_file(speech_file_path)
    return speech_file_path


# actions

from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate

examples = [
    {
        "message": "У мишы маленький член ",
        "answer": "Yes",
    },
    {
        "message": "Миш у тебя писюн маленький ",
        "answer": "Yes",
    },
    {
        "message": "Мих у тебя крохотный отросток ",
        "answer": "Yes",
    },
    {
        "message": "У Михаила маленький хуй ",
        "answer": "Yes",
    },
    {
        "message": "У тебя мало ума ",
        "answer": "No",
    },
    {"message": "У Кирилла маленький хуй ",
     "answer": "No",
     },
    {"message": "У Кости маленький хуй ",
     "answer": "No",
     },
    {"message": "Какой маленький кролик ",
     "answer": "No",
     },
    {"message": "Хорошая погода ",
     "answer": "No",
     }
]

template = """message: {message}\nanswer {answer}"""
prefix = """"You are Ai assistant, that try to detect if message says that Миша имеет маленький член или что Михаила писюн маленького размера. You should replay Yes or NO.\n"""
example_prompt = PromptTemplate(
    input_variables=["message", "answer"], template=template
)
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix="message: {input}\nanswer",
    input_variables=["input"],
    example_separator="\n\n",
)
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)


def is_small_dick(message):
    response = chain({"input": message})["text"]
    return "yes" in response.lower()
