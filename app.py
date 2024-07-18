import json

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import TextLoader

from MenuController import MenuController, menu
from model import llm
from retriever import make_retriever
from shop_data import shop_data

app = Flask(__name__)

cors = CORS(app)

app.register_blueprint(menu)

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

# 1번 api - LLM에게 사용자 입력 전달 후 답변 받기
@app.route('/api/recieve_message', methods=["POST"])
def recieve_message():  # put application's code here

    data = request.json

    user = data.get('user_message', '')

    text = input_message(user)
    response = {
        "success": True,
        "llm_message": text['content'],
        "message_order": text['order_number'],
        "order": text['order']
    }

    return jsonify(response)


def input_message(user):
    demo_ephemeral_chat_history.add_user_message(user)

    # RAG docs 참조
    #docs = rag.invoke(user, embeddings)  # RAG 모델에 질의와 임베딩 전달
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

# 3번 api - 사용자가 선택한 가게 id 전달
@app.route('/api/shop_list/<int:shop_id>', methods=['GET'])
def get_shop_details(shop_id):
    print("/api/shop_list/<int:shop_id>")
    text = input_message("음식을 주문하고 싶어")

    response = {
        "success": True,
        "llm_message": text['content'],
        "message_order": text['order_number'],
        "order": text['order']
    }

    return jsonify(response)


# 5번 api - 사용자가 선택한 메뉴 id 및 메뉴 타입 전달(사용자가 음성이 아닌 터치 등으로 직접 선택시)
@app.route('/api/<shop_name>/menu/<string:menu_type>/<menu_name>', methods=['GET'])
def get_menu_order(shop_name, menu_type, menu_name):
    print("/api/<shop_name>/menu/<string:menu_id>/<menu_name>")
    text = input_message(f"{menu_name}을 주문하고 싶어")

    response = {
        "success": True,
        "llm_message": text['content'],
        "message_order": text['order_number'],
        "order": text['order']
    }

    return jsonify(response)

# 7번 api - 최종 주문서 받아오기
@app.route('/api/<shop_name>/order_list', methods=['GET'])
def get_final_orderlist(shop_name):

    print("/api/<shop_name>/order_list")
    order_response = {
        "order_list": [
            {
                "menu_type": "main",
                "menu_name": "불고기 버거",
                "menu_price": "10000",
                "menu_num": "1",
                "menu_image_url": "http://example.com/images/불고기버거.jpg"
            },
            {
                "menu_type": "side",
                "menu_name": "치킨너겟 4조각",
                "menu_price": "3800",
                "menu_num": "1",
                "menu_image_url": "http://example.com/images/치킨너겟.jpg"
            },
            {
                "menu_type": "side",
                "menu_name": "상하이 치킨랩",
                "menu_price": "5500",
                "menu_num": "2",
                "menu_image_url": "http://example.com/images/상하이치킨랩.jpg"
            },
            {
                "menu_type": "drink",
                "menu_name": "콜라",
                "menu_price": "2000",
                "menu_num": "1",
                "menu_image_url": "http://example.com/images/콜라.jpg"
            }
        ],
        "total_price": "26800"
    }
    return jsonify(order_response)


'''if __name__ == '__main__':
    app.run()'''
