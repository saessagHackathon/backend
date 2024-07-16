import json

from flask import Flask, render_template, request, Response
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import TextLoader

from model import llm
from retriever import make_retriever
from shop_data import shop_data

app = Flask(__name__)

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


@app.route('/chat', methods=["POST"])
def input_post():  # put application's code here

    user = request.json
    print(f"user : {user}")

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
    print(text['content'])

    # 주문 완료시 주문 완료 메세지와 함께 채팅 종료
    if text['order'] == 'complete':
        print('주문이 완료되었습니다. 즐거운 시간되세요!')
        res = json.dumps('주문이 완료되었습니다!', ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')
    else:
        res = json.dumps(text['content'], ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')


if __name__ == '__main__':
    app.run()
