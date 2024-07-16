import json

from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import TextLoader

from model import llm
from retriever import make_retriever
from shop_data import shop_data

app = Flask(__name__)

cors = CORS(app)
shop_name = 'burgerking'

# prompt
shop_prompt = shop_data[shop_name]['prompt']

# db
shop_db = shop_data[shop_name]['db']
print(shop_db)

# 메세지 대화 저장
demo_ephemeral_chat_history = ChatMessageHistory()

# 모델 정의
document_chain = create_stuff_documents_chain(llm, shop_prompt)

# retriever 정의
loader = TextLoader(shop_db, encoding="utf-8")
data = loader.load()
rag = make_retriever(data)


def convert_to_json(content):
    text_split = content[8:].replace('`', "").strip()
    text_json = json.loads(text_split)

    return text_json


@app.route('/', methods=["GET"])
def hello_world():  # put application's code here
    return render_template('chat.html', filename='chat.html')


@app.route('/api/recieve_message', methods=["POST"])
def recieve_message():  # put application's code here

    data = request.json
    user = data.get('user_message', '')

    text = input_message(user)
    response = {
        "success": True,
        "llm_message": text['content'],
        "message_order": text['order_number']
    }

    return jsonify(response)


def input_message(user):
    demo_ephemeral_chat_history.add_user_message(user)

    # RAG docs 참조
    docs = rag.invoke(user)

    # AI 메세지 생성
    content = document_chain.invoke(
        {
            "messages": demo_ephemeral_chat_history.messages,
            "context": docs
        }
    )
    # AI 메세지 저장
    demo_ephemeral_chat_history.add_ai_message(content)

    # str > json
    text = convert_to_json(content)

    # AI 메세지 출력
    print(text)

    return text


@app.route('/api/shop_list', methods=["GET"])
def shop_list():
    shops = [
        {
            "id": 1,
            "shop_name": "버거킹",
            "shop_image_url": "http://example.com/imageA.jpg"
        },
        {
            "id": 2,
            "shop_name": "맥도날드",
            "shop_image_url": "http://example.com/imageB.jpg"
        },
        {
            "id": 3,
            "shop_name": "메가커피",
            "shop_image_url": "http://example.com/imageC.jpg"
        }
    ]

    shops_list = [
        {
            "id": shop["id"],
            "shop_name": shop["shop_name"],
            "shop_image_url": shop["shop_image_url"]
        }
        for shop in shops
    ]
    return jsonify(shops_list)


@app.route('/api/shop_list/<int:shop_id>', methods=['GET'])
def get_shop_details(shop_id):
    text = input_message("음식을 주문하고 싶어")

    response = {
        "success": True,
        "llm_message": text['content'],
        "message_order": text['order_number']
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run()
