import json

from dotenv import load_dotenv
from api.schemas.request.chatbot_request import ChatRequest
from app.chatbot.service import chatbot_service
import os

from app.dit.util import memorial_http_util
load_dotenv()

WRITE_MEMORIAL_PROMPT = "추모관에 댓글 작성할거야."

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

    chat_request = ChatRequest(
        content=WRITE_MEMORIAL_PROMPT
    )

    # chatbot 응답 받기
    chatbot_response = await chatbot_service.chat(chatbot_id=character_id, chat_request=chat_request, user_id=str(memorial_id))

    # memorial 요청 보내기
    response = await memorial_http_util.write_memorial_comment(user_id=str(character_id), memorial_id=memorial_id, content=chatbot_response.answer)
    return response

if __name__ == '__main__':
    import asyncio
    import pprint
    response = asyncio.run(write_memorial(character_id=1, memorial_id=103))
    print(response)
    print("-------------------")
    pprint(response)



