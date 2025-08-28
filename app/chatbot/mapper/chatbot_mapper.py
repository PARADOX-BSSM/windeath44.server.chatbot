from collections import Counter

from api.schemas.response.chatbot_response import ChatBotResponse
from app.chatbot.document.chatbot import ChatBot


async def to_chatbot_response(chatbot : ChatBot) -> ChatBotResponse:
    counter = Counter(chatbot.contributors)
    sorted_contributors = [item for item, _ in counter.most_common()] # 중복 제거 및 많이 기여한 순서대로 정렬

    chatbot_response = ChatBotResponse(chatbot_id=chatbot.id, name=chatbot.name, contributor=sorted_contributors, description=chatbot.description)
    return chatbot_response

