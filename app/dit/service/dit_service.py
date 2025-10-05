import json

from dotenv import load_dotenv
from api.schemas.request.chatbot_request import ChatRequest
from app.chatbot.service import chatbot_service
import os

from app.dit.util import memorial_http_util
load_dotenv()

WRITE_MEMORIAL_PROMPT = """
지금 당신은 팬이 만든 추모관을 보고 댓글을 작성하려 합니다.

[추모관 내용]
{contentdnjanjwdadn}

[받은 절 횟수]
{bowedmajondai}

위 내용을 읽고, 당신의 감정이 자연스럽게 추모 댓글을 작성하세요.  
"""

memorial_domain = os.getenv("MEMORIAL_DOMAIN")

# characterId,
# bowCount,
# memorialCommitId,
# content,
# createdAt,
# updatedAt


async def write_memorial(character_id : int, memorial_id : int):
    # 1. 추모관 글 조회
    # 2. 추모관 글을 토대로 프롬프트 구성
    # 3. 챗봇 응답 받기
    # 4. 글 작성 요청 보내기

    # 추모관 글 조회
    memorial_content = await memorial_http_util.get_memorial_content(memorial_id=memorial_id)

    # prompt 구성
    prompt = (
        WRITE_MEMORIAL_PROMPT
        .replace("{contentdnjanjwdadn}", memorial_content["content"])
        .replace("{bowedmajondai}", str(memorial_content["bowCount"]))
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



