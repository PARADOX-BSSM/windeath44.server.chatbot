from api.schemas.response.chatbot_response import ChatBotResponse, ContributorResponse
from domain.documents.chatbot import ChatBot


async def to_chatbot_response(chatbot : ChatBot) -> ChatBotResponse:
    contributor = [ContributorResponse(contributor_id=wordset.contributor) for wordset in chatbot.character_wordset]
    chatbot_response = ChatBotResponse(chatbot_id=chatbot.id, name=chatbot.name, contributor=contributor)
    return chatbot_response