import json

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import TextLoader
import logging

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


@app.route('/api/shop_list', methods=["GET"])
def shop_list():
    print("/api/shop_list")
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
    print("/api/shop_list/<int:shop_id>")
    text = input_message("음식을 주문하고 싶어")

    response = {
        "success": True,
        "llm_message": text['content'],
        "message_order": text['order_number'],
        "order": text['order']
    }

    return jsonify(response)

@app.route('/api/<shop_name>/menu/<string:menu_id>', methods=['GET'])
def get_menu_details(shop_name, menu_id):
    print("/api/<shop_name>/menu/<string:menu_id>")
    if menu_id == "main":
        menus = [
            {
                "id": 1,
                "menu_name": "불고기 버거",
                "menu_price": "10000",
                "menu_image_url": "http://example.com/images/불고기버거.jpg",
                "menu_type": "main",
                "menu_tag": [
                    {
                        "tag_id": "1",
                        "tag_content": "불고기 패티"
                    },
                    {
                        "tag_id": "2",
                        "tag_content": "달달함"
                    }
                ],
            },
            {
                "id": 2,
                "menu_name": "치즈 버거",
                "menu_price": "5000",
                "menu_image_url": "http://example.com/images/치즈버거버거.jpg",
                "menu_type": "main",
                "menu_tag": [
                    {
                        "tag_id": "1",
                        "tag_content": "치즈 패티"
                    },
                    {
                        "tag_id": "2",
                        "tag_content": "느끼함"
                    }
                ],
            }
        ]
    elif menu_id == "side":
        menus = [
            {
                "id": 1,
                "menu_name": "감자튀김",
                "menu_price": "2000",
                "menu_image_url": "http://example.com/images/감자튀김.jpg",
                "menu_type": "side",
                "menu_tag": [
                    {
                        "tag_id": "1",
                        "tag_content": "감자"
                    }
                ]
            },
            {
                "id": 2,
                "menu_name": "치즈스틱",
                "menu_price": "2500",
                "menu_image_url": "http://example.com/images/치즈스틱.jpg",
                "menu_type": "side",
                "menu_tag": [
                    {
                        "tag_id": "1",
                        "tag_content": "모자렐라"
                    }
                ]
            }
        ]
    elif menu_id == "drink":
        menus = [
            {
                "id": 1,
                "menu_name": "콜라",
                "menu_price": "1500",
                "menu_image_url": "http://example.com/images/콜라.jpg",
                "menu_type": "drink",
                "menu_tag": [
                    {
                        "tag_id": "1",
                        "tag_content": "설탕 제로"
                    }
                ]
            },
            {
                "id": 2,
                "menu_name": "사이다",
                "menu_price": "1500",
                "menu_image_url": "http://example.com/images/사이다.jpg",
                "menu_type": "drink",
                "menu_tag": [
                    {
                        "tag_id": "1",
                        "tag_content": "설탕 제로"
                    }
                ]
            }
        ]

    menu_list = [
        {
            "id": menu["id"],
            "menu_name": menu["menu_name"],
            "menu_price": menu["menu_price"],
            "menu_image_url": menu["menu_image_url"],
            "menu_type": menu["menu_type"],
            "menu_tag": [
                {
                    "tag_id": tag["tag_id"],
                    "tag_content": tag["tag_content"]
                }
                for tag in menu["menu_tag"]
            ]
        }
        for menu in menus
    ]

    return jsonify(menu_list)


@app.route('/api/<shop_name>/menu/<string:menu_id>/<menu_name>', methods=['GET'])
def get_menu_order(shop_name, menu_id, menu_name):
    print("/api/<shop_name>/menu/<string:menu_id>/<menu_name>")
    text = input_message(f"{menu_name}을 주문하고 싶어")

    response = {
        "success": True,
        "llm_message": text['content'],
        "message_order": text['order_number'],
        "order": text['order']
    }

    return jsonify(response)


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


if __name__ == '__main__':
    app.run()
