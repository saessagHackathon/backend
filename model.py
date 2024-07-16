from langchain_community.chat_models import ChatOpenAI
from prompt import question_answering_prompt

from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.environ.get('API_KEY')
llm = ChatOpenAI(
    model='gpt-4o',
    api_key=API_KEY
)

document_chain = create_stuff_documents_chain(llm, question_answering_prompt)
