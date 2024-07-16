from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.openai import OpenAIEmbeddings
from model import API_KEY


loader = TextLoader('mydata.txt', encoding="utf-8")
data = loader.load()
    
text_splitter = CharacterTextSplitter(
    separator = '\n',
    chunk_size = 30,
    chunk_overlap  = 10,
    length_function = len,
)

texts = text_splitter.split_text(data[0].page_content)

embeddings_model = OpenAIEmbeddings(
    api_key = API_KEY
)
db = Chroma.from_texts(
    texts, 
    embeddings_model,
    collection_name = 'history',
    persist_directory = './db/chromadb',
    collection_metadata = {'hnsw:space': 'cosine'}, 
)
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5}) 