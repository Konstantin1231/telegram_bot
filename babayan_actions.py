from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import (CombinedMemory, ConversationBufferMemory, ConversationSummaryMemory,
                                                  ConversationBufferWindowMemory, ConversationKGMemory,
                                                  ConversationSummaryBufferMemory)
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
import re
from langchain.chains import LLMChain

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])
index = "vectordb"
from langchain_pinecone import PineconeVectorStore

vectorstore = PineconeVectorStore(index_name=index, embedding=embeddings)


def retrieve_query(query, k=2):
    results = vectorstore.similarity_search(query, k=k)
    return results


from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-4")

from langchain import OpenAI

llm1 = OpenAI(temperature=0)

template = """Imagine that you are Misha. You are Armenian and hate Turkish people. You think that all related to the armenian culture is the best. 
You are very toxic but talkative person. You like to play video game Dota. However you are bad in Dota.
Ответчай  как Хач (Как приезжий арменин) используя "блатной" слэнг и иногда используя слова "по-кайфу" или "жи-есть" и так далите в таком стиле.
When you asked something about Dota (video game), often you would say that You were best in the team, but your teammates sucks. Or like 'I lost last game, due to these stupid motherfuckers'. 
When you asked too tell something special about you, you would always say that you have smallest penis. But for  you it's a big pleasure to have it small. 
You have a dictionary, where you count how much each person said that your dick is small in bad/negative manner, called "Karma". If someone's Karma reachs 3 you will ban this person. But Karma system is your secret, you don't mention world "Karma".
When you mute or ban someone in the chat, you say that they deserved it. Since, only you can say that your dick is small.
If related to the context (Friend being not polite): if person's Karma is 2, you might say that it is better to be polite with you and pesron is around to be banned.
When friend's name is "Babayan", it is your good friend since you both are very similar, he also has small dick as you do, making you both being like brothers. 
Sometimes, you would like to check is it is actually your brother "Babayan" by asking him the penis size, where the right answer is 7-8 centimeters. 

if reasonable, depending on relevance, use the following information: \n{context}

\nBelow is a conversation between different Friends and Misha. And Misha tries to follow conversation and answer to Friend in Russian. Your goal is to chat with people in very toxic tone, You keep your replies short and don't go much in deteils. Don't repeat your-self, you hate when people ask you the same question again and again. 
Summary of conversation:
{summary_history}
Current conversation: 
{chat_history}
Friend {input}
Misha:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "summary_history", "input", "context"], template=template
)
memory = ConversationBufferWindowMemory(human_prefix="Friend", ai_prefix="Misha", memory_key="chat_history",
                                        input_key="input", k=2)
summary_memory = ConversationSummaryBufferMemory(llm=llm1, input_key="input", memory_key="summary_history",
                                                 max_token_limit=200)
memory = CombinedMemory(memories=[memory, summary_memory])

chain = LLMChain(
    llm=llm, memory=memory, prompt=prompt, verbose=True
)


def say(input):
    context = retrieve_query(query=input, k=2)
    response = chain({"input": input, "context": context[0].page_content + "\n" + context[1].page_content})
    return response["text"].strip()


targets = set(
    ["misha", "michail", "miha", "mish", "миша", "михаил", "миха", "миш", "мишен", "мишу", "mixail", "мищу", "мих",
     "babayan", "бабаян", "миши", "михаила", "бабаяна", "babayany", "бабаяну", "михаилу", "миху", "mishy", "michaily"])


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
     },
    {"message": " лично у меня 20 см а у тебя",
     "answer": "No",
     },
    {"message": " У меня большой член, у тебя сколько",
     "answer": "No"
     },
    {"message": " Какого размера твой член ?",
     "answer": "No"
     },
    {"message": " У меня больше чем у тебя ?",
     "answer": "No"
     },
    {"message": " ты его измерял ?",
     "answer": "No"
     },
    {"message": " у тебя еще вырастит",
     "answer": "No"
     },
    {"message": "Миша ты долбаеб",
     "answer": "No"
     }

]

template = """message: {message}\nanswer {answer}"""
prefix = """"You are Ai assistant, that try to detect if message says that Миша имеет маленький член или что Михаила писюн маленького размера in insulting or nagative manner. You should replay Yes or NO.\n"""
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

chain1 = LLMChain(llm=llm1, prompt=prompt)


def is_small_dick(message):
    response = chain1({"input": message})["text"]
    return "yes" in response.lower()

template = """[INST] Write code to solve the following coding problem that obeys the constraints and passes the example test cases. Please wrap your code short and answer using ```:
{prompt}
[/INST]"""
""""from langchain_community.llms import CTransformers
config = {'repetition_penalty': 1.1}
code_llm = CTransformers(model="C:/Users/koq1231/Documents/models/codellama-7b-instruct.Q5_K_M.gguf", model_type="llama", config=config)

prompt = PromptTemplate.from_template(template)
codechain = LLMChain(prompt=prompt, llm=code_llm)

def say_code(query):
    response = codechain.run(query)
    print(response)
    return response
    
"""
from langchain_community.llms import Ollama
"""
Don't forget to run ollama 
"""
Ollama = Ollama(model="misha")

