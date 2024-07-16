import json
import re

from flask import Flask, render_template, request, Response
from langchain_community.chat_message_histories import ChatMessageHistory
from model import document_chain
from retriever import retriever

app = Flask(__name__)
demo_ephemeral_chat_history = ChatMessageHistory()


@app.route('/', methods=["GET"])
def hello_world():  # put application's code here
    return render_template('chat.html', filename='chat.html')


@app.route('/chat', methods=["POST"])
def input_post():  # put application's code here

    user = request.json
    print(f"user : {user}")
    demo_ephemeral_chat_history.add_user_message(user)
    docs = retriever.invoke(user)
    content = document_chain.invoke(
        {
            "messages": demo_ephemeral_chat_history.messages,
            "context": docs,
        }
    )
    demo_ephemeral_chat_history.add_ai_message(content)

    if 'json' not in content:
        print(f"content : {content}")
        res = json.dumps(content, ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')
    else:
        json_str = re.search(r'```json\n(.*)```', content, re.DOTALL).group(1)
        print('주문이 완료되었습니다!')
        order_dict = json.loads(json_str)

        res = json.dumps('주문이 완료되었습니다!', ensure_ascii=False).encode('utf8')
        return Response(res, content_type='application/json; charset=utf-8')


'''if __name__ == '__main__':
    app.run()
'''