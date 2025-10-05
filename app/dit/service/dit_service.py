import json

from dotenv import load_dotenv
from api.schemas.request.chatbot_request import ChatRequest
from app.chatbot.service import chatbot_service
import os

from app.dit.util import memorial_http_util
from core.grpcs.client.chatbot_grpc_client import ChatbotGrpcClient

load_dotenv()

WRITE_MEMORIAL_PROMPT = """
지금 당신은 팬이 만든 추모관을 보고 댓글을 작성하려 합니다.

[추모관 캐릭터 정보]
이름 : {name}
생전에 했던 명언 : {saying}
출연한 애니메이션 이름 : {anime_name}

[추모관 내용]
{content}

[받은 절 횟수]
{bow}

위 내용을 읽고, 당신의 감정이 자연스럽게 추모 댓글을 작성하세요.  
"""

async def write_memorial(character_id : int, memorial_id : int, chatbot_grpc_client : ChatbotGrpcClient):
    # 1. 추모관 조회
    # 1.1 추모관 글 조회
    # 1.2 추모관 캐릭터 조회
    # 2. 추모관 글을 토대로 프롬프트 구성
    # 3. 챗봇 응답 받기
    # 4. 글 작성 요청 보내기

    # 추모관 글 조회
    memorial_content = await memorial_http_util.get_memorial_content(memorial_id=memorial_id)

    # 추모관 캐릭터 조회
    memorial_character = await chatbot_grpc_client.get_character(character_id=memorial_content["characterId"])
    # animeId = 1
    # animeName = 2
    # name = 3
    # content = 4
    # state = 5

    # prompt 구성
    prompt = (
        WRITE_MEMORIAL_PROMPT
        .replace("{content}", memorial_content["content"])
        .replace("{bow}", str(memorial_content["bowCount"]))
        .replace("{name}", memorial_character.name)
        .replace("{anime_name}", memorial_character.animeName)
        .replace("{saying}", memorial_character.content)
    )
    print(prompt)
    chat_request = ChatRequest(
        content=prompt
    )

    # chatbot 응답 받기
    chatbot_response = await chatbot_service.chat(chatbot_id=character_id, chat_request=chat_request, user_id=str(memorial_id))

    # memorial 글 작성
    response = await memorial_http_util.write_memorial_comment(user_id=str(character_id), memorial_id=memorial_id, content=chatbot_response.answer)
    return response

if __name__ == '__main__':
    import asyncio
    import pprint
    response = asyncio.run(write_memorial(character_id=1, memorial_id=103))
    print(response)
    print("-------------------")
    pprint(response)



