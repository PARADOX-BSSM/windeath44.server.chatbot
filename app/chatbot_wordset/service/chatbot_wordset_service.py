from api.schemas.common.response.cursor_response import CursorResponse
from api.schemas.request.chatbot_wordset_request import ChatBotWordIdsRequest
from app.chatbot_wordset.repository import chatbot_wordset_repo
from app.chatbot_wordset.document.wordset_status import WordSetStatus
from app.chatbot.document.chatbot import CharacterWordSet
from app.chatbot.repository import chatbot_repo
from app.chatbot_wordset.exception.already_approved_wordset_exception import AlreadyApprovedWordSetException


async def add(character_id : int, chatbot_wordset_request : ChatBotWordIdsRequest, user_id : str):
    await chatbot_wordset_repo.save(character_id, chatbot_wordset_request, user_id)


async def get_chatbot_wordset(cursor_id : int, size : int) -> CursorResponse:
    chatbot_wordset = await chatbot_wordset_repo.find(size) if cursor_id is None else await chatbot_wordset_repo.find_by_cursor_id(cursor_id, size)
    has_next = len(chatbot_wordset) > size
    return CursorResponse(hasNext=has_next, values=chatbot_wordset[:size])


async def get_chatbot_wordset_by_character(character_id : int, cursor_id : int, size : int) -> CursorResponse:
    chatbot_wordset = await chatbot_wordset_repo.find_by_character_id(character_id, size) if cursor_id is None else await chatbot_wordset_repo.find_by_cursor_id_and_character_id(character_id, cursor_id, size)
    has_next = len(chatbot_wordset) > size
    return CursorResponse(hasNext=has_next, values=chatbot_wordset[:size])



async def approve_wordset(wordset_id: str):
    """말투셋 승인 및 챗봇에 추가"""
    # wordset 조회
    wordset = await chatbot_wordset_repo.find_by_id(wordset_id)
    
    # 이미 승인된 경우 예외 발생
    if wordset.status == WordSetStatus.APPROVED:
        raise AlreadyApprovedWordSetException(wordset_id=wordset_id)
    
    # 상태 업데이트
    wordset = await chatbot_wordset_repo.update_status(wordset_id, WordSetStatus.APPROVED)
    
    # 챗봇의 character_wordset에 추가
    character_wordset = CharacterWordSet(
        question=wordset.question,
        answer=wordset.answer,
        contributor=wordset.writer_id
    )
    
    # 챗봇에 wordset 추가
    await chatbot_repo.add_wordset(wordset.character_id, character_wordset, wordset.writer_id)


async def reject_wordset(wordset_id: str):
    """말투셋 거절"""
    
    # wordset 조회 및 상태 업데이트
    await chatbot_wordset_repo.update_status(wordset_id, WordSetStatus.REJECTED)



async def delete_wordset(wordset_id: str):
    """말투셋 삭제 (챗봇에서도 제거)"""
    # wordset 조회
    wordset = await chatbot_wordset_repo.find_by_id(wordset_id)
    
    # 챗봇에서 해당 wordset 제거 (승인된 경우에만)
    if wordset.status == WordSetStatus.APPROVED:
        await chatbot_repo.remove_wordset(
            wordset.character_id,
            wordset.question,
            wordset.answer
        )
    
    # wordset 삭제
    await chatbot_wordset_repo.delete_by_id(wordset_id)


async def get_chatbot_wordset_with_status(cursor_id: int, size: int, status: str = None) -> CursorResponse:
    """상태별 wordset 조회"""
    if status:
        chatbot_wordset = (
            await chatbot_wordset_repo.find_by_status(status, size)
            if cursor_id is None
            else await chatbot_wordset_repo.find_by_cursor_id_and_status(cursor_id, status, size)
        )
    else:
        chatbot_wordset = (
            await chatbot_wordset_repo.find(size)
            if cursor_id is None
            else await chatbot_wordset_repo.find_by_cursor_id(cursor_id, size)
        )
    
    has_next = len(chatbot_wordset) > size
    return CursorResponse(hasNext=has_next, values=chatbot_wordset[:size])


async def get_chatbot_wordset_by_character_with_status(
    character_id: int, cursor_id: int, size: int, status: str = None
) -> CursorResponse:
    """캐릭터별, 상태별 wordset 조회"""
    if status:
        chatbot_wordset = (
            await chatbot_wordset_repo.find_by_character_id_and_status(character_id, status, size)
            if cursor_id is None
            else await chatbot_wordset_repo.find_by_cursor_id_character_id_and_status(
                character_id, cursor_id, status, size
            )
        )
    else:
        chatbot_wordset = (
            await chatbot_wordset_repo.find_by_character_id(character_id, size)
            if cursor_id is None
            else await chatbot_wordset_repo.find_by_cursor_id_and_character_id(character_id, cursor_id, size)
        )
    
    has_next = len(chatbot_wordset) > size
    return CursorResponse(hasNext=has_next, values=chatbot_wordset[:size])
