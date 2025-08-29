from collections import Counter
from typing import List

from api.schemas.response.chatbot_response import ChatBotResponse, ChatBotDetailsResponse, CharacterWordSetResponse
from app.chatbot.document.chatbot import ChatBot


async def to_chatbot_response(chatbot : ChatBot) -> ChatBotResponse:
    sorted_contributors = await _sort_contributors_by_count(chatbot.contributors)

    chatbot_response = ChatBotResponse(chatbot_id=chatbot.id, name=chatbot.name, contributor=sorted_contributors, description=chatbot.description)
    return chatbot_response


async def to_chatbot_details_response(chatbot : ChatBot) -> ChatBotDetailsResponse:
    sorted_contributors = await _sort_contributors_by_count(chatbot.contributors)
    chatbot_wordset = [CharacterWordSetResponse(question=wordset.question, answer=wordset.answer, contributor=wordset.contributor) for wordset in chatbot.character_wordset]
    chatbot_detils_response = ChatBotDetailsResponse(chatbot_id=chatbot.id, name=chatbot.name, description=chatbot.description, contributor=sorted_contributors, chatbot_wordset=chatbot_wordset)
    return chatbot_detils_response


async def _sort_contributors_by_count(contributors : List[str]):
    counter = Counter(contributors)
    sorted_contributors = [item for item, _ in counter.most_common()]  # 중복 제거 및 많이 기여한 순서대로 정렬
    return sorted_contributors

