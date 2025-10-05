from dotenv import load_dotenv
from api.schemas.request.chatbot_request import ChatRequest
from app.chatbot.service import chatbot_service
import os

from app.dit.util import memorial_http_util
load_dotenv()

WRITE_MEMORIAL_PROMPT = ""

memorial_domain = os.getenv("MEMORIAL_DOMAIN")

# characterId,
# bowCount,
# memorialCommitId,
# content,
# createdAt,
# updatedAt

async def write_memorial(character_id : int, memorial_id : int):
    chat_request = ChatRequest(
        content=WRITE_MEMORIAL_PROMPT
    )

    chatbot_response = await chatbot_service.chat(chatbot_id=character_id, chat_request=chat_request, user_id=str(memorial_id))

    # memorial 요청 보내기
    await memorial_http_util.write_memorial_comment(user_id=str(character_id), memorial_id=memorial_id, content=chatbot_response.answer)



