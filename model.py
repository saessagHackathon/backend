import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
#from langchain_community.chat_models import ChatOpenAI


load_dotenv()

API_KEY = os.environ.get('API_KEY')
llm = ChatOpenAI(
    model='gpt-4o-mini',
    api_key=API_KEY
)

