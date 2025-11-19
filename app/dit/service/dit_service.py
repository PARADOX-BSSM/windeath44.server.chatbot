import json

from dotenv import load_dotenv
from api.schemas.request.chatbot_request import ChatRequest
from api.schemas.response.chatbot_response import ChatResponse
from app.chatbot.service import chatbot_service
import os

from app.dit.util import memorial_http_util
from core.grpcs.client.chatbot_grpc_client import ChatbotGrpcClient
from slugify import slugify

load_dotenv()

WRITE_MEMORIAL_PROMPT = """
당신은 지금 {name}의 추모관을 방문했습니다.
아래는 추모관에 대한 상세 정보입니다.

[캐릭터 정보]
- 이름: {name}
- 생전에 남긴 명언: {saying}
- 출연 작품: {anime_name}

[추모관 내용]
{content}

[받은 절 횟수]
{bow}

[인기 추모글 예시]
{popular_comments}

위의 정보를 바탕으로, 당신이 느낀 감정에 따라 자연스럽게 추모글을 남겨주세요.
"""


async def write_memorial(character_id : int, memorial_id : int, chatbot_grpc_client : ChatbotGrpcClient) -> ChatResponse:
    # 1. 추모관 조회
    # 1.1 추모관 글 조회
    # 1.2 추모관 캐릭터 조회
    # 2. 추모관 글을 토대로 프롬프트 구성
    # 3. 챗봇 응답 받기
    # 4. 글 작성 요청 보내기

    # 추모관 글 조회
    memorial_content = await memorial_http_util.get_memorial_content(memorial_id=memorial_id)
    
    # 인기 댓글 조회
    popular_comments = await memorial_http_util.get_popular_comments(
        memorial_id=memorial_id, 
        user_id=str(character_id),
        size=5
    )

    # 추모관 캐릭터 조회
    memorial_character = await chatbot_grpc_client.get_character(character_id=memorial_content["characterId"])

    # 프롬프트 구성
    # 인기 댓글 포맷팅
    popular_comments_text = "".join([
        f"- {comment.get('content', '')} (작성자: {comment.get('userId', '알 수 없음')}, 좋아요 {comment.get('likes', 0)}개, {comment.get('createdAt', '날짜 정보 없음')})\n"
        for comment in popular_comments
    ]) if popular_comments else "인기 댓글이 없습니다."
    
    prompt = (
        WRITE_MEMORIAL_PROMPT
        .replace("{content}", memorial_content["content"])
        .replace("{bow}", str(memorial_content["bowCount"]))
        .replace("{name}", memorial_character.name)
        .replace("{anime_name}", memorial_character.animeName)
        .replace("{saying}", memorial_character.content)
        .replace("{popular_comments}", popular_comments_text)
    )
    print(prompt)
    chat_request = ChatRequest(
        content=prompt
    )

    # chatbot 응답 받기
    chatbot_response = await chatbot_service.dit_chat(chatbot_id=character_id, chat_request=chat_request, user_id=str(memorial_id))

    chatbot = await chatbot_service.find_chatbot(chatbot_id=character_id)
    # 추모관에 표시되는 chatbot id
    memorial_chatbot_user_id = f"official-windeath44-{slugify(chatbot.name)}"

    # memorial 글 작성
    response = await memorial_http_util.write_memorial_comment(user_id=memorial_chatbot_user_id, memorial_id=memorial_id, content=chatbot_response.answer)
    return chatbot_response



