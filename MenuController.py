import os

import pandas as pd
import pymysql.cursors
from dotenv import load_dotenv
from flask import jsonify, Blueprint

# from langchain_community.chat_models import ChatOpenAI


load_dotenv()

menu = Blueprint('MenuController', __name__)


def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('db_host'),
        port=int(os.environ.get('db_port')),
        user=os.environ.get('db_user'),
        passwd=os.environ.get('db_passwd'),
        db='leaf_hackton', charset='utf8'
    )


class MenuController:
    # 2번 api - 가게 리스트 받아오기
    @menu.route('/api/shop_list', methods=["GET"])
    def shop_list():
        print("/api/shop_list")

        db = get_db_connection()
        cursor = db.cursor()

        sql = "select * from shoplist"  # DB 조회
        cursor.execute(sql)

        # DB에서 조회한 데이터를 머신러닝하기 쉽도록 데이터프레임 형태로 변환
        data = cursor.fetchall()
        dataSet = pd.DataFrame(data)
        dataSet.columns = ['id', 'shop_name', 'shop_image_url']
        dataSet['id'] = pd.to_numeric(dataSet['id'])

        db.close()

        '''shops = [
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
                ]'''

        shops_list = dataSet.to_dict(orient='records')

        print(shops_list)
        return jsonify(shops_list)

    # 4번 api - {가게이름}의 메뉴 리스트 및 정보 받아오기
    @menu.route('/api/<shop_name>/menu/<string:menu_type>', methods=['GET'])
    def get_menu_details(shop_name, menu_type):
        print(f"/api/{shop_name}/menu/{menu_type}")
        db = get_db_connection()
        cursor = db.cursor(pymysql.cursors.DictCursor)

        sql = """
            SELECT 
                m.id AS menu_id,
                m.shop_name,
                m.menu_name,
                m.menu_price,
                m.menu_image_url,
                m.menu_type,
                t.tag_id,
                t.tag_content
            FROM 
                menulist m
            LEFT JOIN 
                menu_tags t ON m.shop_name = t.shop_name AND m.menu_name = t.menu_name
            WHERE 
                m.shop_name = %s AND m.menu_type = %s;
            """
        cursor.execute(sql, (shop_name, menu_type))
        data = cursor.fetchall()
        db.close()

        menu_dict = {}
        for row in data:
            menu_id = row['menu_id']
            if menu_id not in menu_dict:
                menu_dict[menu_id] = {
                    "id": menu_id,
                    "shop_name": row['shop_name'],
                    "menu_name": row['menu_name'],
                    "menu_price": str(int(row['menu_price'])),
                    "menu_image_url": row['menu_image_url'],
                    "menu_type": row['menu_type'],
                    "menu_tag": []
                }
            if row['tag_id'] is not None:  # Check if there are tags
                menu_dict[menu_id]['menu_tag'].append({
                    "tag_id": row['tag_id'],
                    "tag_content": row['tag_content']
                })

        menu_list = list(menu_dict.values())

        return jsonify(menu_list)

    '''
        if menu_type == "main":
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
        elif menu_type == "side":
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
        elif menu_type == "drink":
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

        return jsonify(menu_list)'''
