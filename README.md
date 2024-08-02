# api 목록

1. `POST /api/recieve_message` - LLM에게 사용자 입력 전달 후 답변 받기
2. `GET /api/shop_list` - 가게 리스트 받아오기
3. `GET /api/shop_list/{shop_id}` - 사용자가 선택한 가게 id 전달
4. `GET /api/{가게이름}/menu/{menu_type}` - {가게이름}의 메뉴 리스트 및 정보 받아오기
5. `GET /api/{가게이름}/menu/{menu_type}/{menu_id}` - 사용자가 선택한 메뉴 id 및 메뉴 타입 전달(사용자가 음성이 아닌 터치 등으로 직접 선택시)
6. `POST /api/{가게이름}/menu` - 사용자가 선택한 메뉴 id 및 메뉴 타입 전달 (사용자가 음성으로 메뉴 선택시)
7. `GET /api/{가게이름}/order_list` - 최종 주문서 받아오기

## 1. `POST /api/recieve_message`

![1](https://github.com/user-attachments/assets/e2aa6e94-cb72-4788-a1f0-ac9b23910542)


- LLM에게 사용자 입력 전송 및 답변 받아오기
- 받아온 “message_order”를 바탕으로 메뉴 조회 api인 `GET /api/{가게이름}/menu/{menu_type}`가 실행됨

### Request

```json
{
    "user_message" : {유저의 메시지를 전달}
}

```

### Response

```json
{
	"success": true,
	"llm_message": {llm이 생성한 답변을 전달},
	"message_order": {현재 진행중인 템플릿 순서를 전달},
	"order": {ordring, final_check, complete로 주문 상태를 전달}
}
```

## `2. GET /api/shop_list`

![2](https://github.com/user-attachments/assets/fe03d7c9-fa0b-4171-b2fb-2458e2473ad0)


전체 가게 리스트를 조회

### Response

```json
[
    {
        "id": 1,
        "shop_name": "맥도날드",
        "shop_image_url": "http://example.com/images/맥도날드.jpg"
    },
    {
        "id": 2,
        "shop_name": "롯데리아",
        "shop_image_url": "http://example.com/images/롯데리아.jpg"
    },
	...
	
]
```

## 3.`GET /api/shop_list/{shop_id}`

사용자가 선택한 가게 id를 전달 받는 엔드포인트.

- 벡엔드 측에서 가게 id에 해당하는 특정 프롬포트로 변환 및 가게 정보 등을 LLM에게 전달하는 등 기초 설정을 할때 이용
- 화면단에선 주문 페이지로 이동

### response

```json
{
	"success": true,
	"llm_message": {기본 메시지 반환 ex) 안녕하세요, 맥도날드 입니다. 무엇을 도와드릴까요?},
	"message_order": {현재 진행중인 템플릿 순서를 전달},
	"order": {ordring, final_check, complete로 주문 상태를 전달}
}
```

## 4.`GET /api/{가게이름}/menu/{menu_type}`

![3](https://github.com/user-attachments/assets/a9ebbe71-3b7c-4365-bc83-f443fff67b3d)


- 선택한 가게의 메뉴 리스트 조회
- menu_type에 따라 메인 메뉴, 사이드 메뉴, 음료 메뉴 등의 list를 전달 받음
- 현재 진행중인 템플릿 순서(message_order)에 따라 menu_type의 값을 main, side, drink로 전송

### response

```json
[
    {
        "id": 1,
        "menu_name": "불고기 버거",
        "menu_price" : "10000",
        "menu_image_url": "http://example.com/images/불고기버거.jpg",
        "menu_type" : "main",
        "menu_tag" :
	         {
		         {
			         "tag_id" : "1",
			         "tag_content" : "불고기 패티",
		         },
	        	 {
			         "tag_id" : "2",
			         "tag_content" : "달달함",
		         }
					},
    },
    {
        "id": 2,
        "menu_name": "치즈 버거",
        "menu_price" : "5000",
        "menu_image_url": "http://example.com/images/치즈버거버거.jpg",
        "menu_type" : "main",
        "menu_tag" :
	         {
		         {
			         "tag_id" : "1",
			         "tag_content" : "치즈 패티",
		         },
	        	 {
			         "tag_id" : "2",
			         "tag_content" : "느끼함",
		         }
					},
    },
	...
	
]
```

## 5.`GET /api/{가게이름}/menu/{menu_type}/{menu_id}`

- 사용자가 선택한 메뉴를 전송
- 사용자가 특정 메뉴를 터치로 선택시 작동 → 벡엔드 측에서 선택한 메뉴를 /api/recieve_message로 직접 전달할 예정
- 최종 주문서 작성시 사용

### Response

```json
{
	"success": true,
	"llm_message": {llm이 생성한 답변을 전달},
	"message_order": {현재 진행중인 템플릿 순서를 전달},
	"order": {ordring, final_check, complete로 주문 상태를 전달}
}
```

## 6.`POST /api/{가게이름}/menu`

- 사용자의 답변 및 메뉴 타입(메인 메뉴, 사이드 메뉴, 음료 메뉴 여부)를 전송
- 사용자가 특정 메뉴를 음성으로 선택시 작동
    - 현재 “message_order”를 기준으로 실행
    - 벡엔드 측에서 사용자의 답변에서 선택된 메뉴를 찾아 적재할 예정
- 최종 주문서 작성시 사용

### request

```json
{
    "menu_name" : {유저의 메시지를 전달},
    "menu_type" : "main"
}
```

### response

```json
{
	"success": true,
	"llm_message": {llm이 생성한 답변을 전달},
	"message_order": {현재 진행중인 템플릿 순서를 전달},
	"order": {ordring, final_check, complete로 주문 상태를 전달}
}
```

## 7.`GET /api/{가게이름}/order_list`

![4](https://github.com/user-attachments/assets/cb4e1e17-8550-4ded-8f9d-50a29ced7163)


- 최종 주문서 조회

### response

```json
{
	"order_list" :
	    {
	        "menu_type": "main",
	        "menu_name": "불고기 버거",
	        "menu_price" : "10000",
	        "menu_num" : "1",
	        "menu_image_url": "http://example.com/images/불고기버거.jpg"
	    },
	    {
	        "menu_type": "side",
	        "menu_name": "치킨너겟 4조각",
	        "menu_price" : "3800",
	        "menu_num" : "1",
	        "menu_image_url": "http://example.com/images/치킨너겟.jpg"
	    },
	        {
	        "menu_type": "side",
	        "menu_name": "상하이 치킨랩",
	        "menu_price" : "5500",
	        "menu_num" : "2",
	        "menu_image_url": "http://example.com/images/상하이치킨랩.jpg"
	    },
	    {
	        "menu_type": "drink",
	        "menu_name": "콜라",
	        "menu_price" : "2000",
	        "menu_num" : "1",
	        "menu_image_url": "http://example.com/images/콜라.jpg"
	    },
    },
    {
	    "total_price" : "26800"
    }
]
```
