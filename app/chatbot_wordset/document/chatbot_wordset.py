from datetime import datetime
from beanie import Document, before_event, Insert, Update
from app.chatbot_wordset.document.wordset_status import WordSetStatus


class ChatBotWordSet(Document):
    character_id: int
    question: str
    answer: str
    writer_id: str
    status: WordSetStatus = WordSetStatus.PENDING

    class Settings:
        name = "chat_bot_wordset"