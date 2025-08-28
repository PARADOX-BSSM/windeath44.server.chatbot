from api.schemas.response.chatbot_response import ChatBotResponse
from app.chatbot.document.chatbot import ChatBot


async def to_chatbot_response(chatbot : ChatBot) -> ChatBotResponse:
    chatbot_response = ChatBotResponse(chatbot_id=chatbot.id, name=chatbot.name, contributor=chatbot.contributors)
    return chatbot_response

