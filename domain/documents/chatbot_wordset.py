from beanie import Document


class ChatBotWordSet(Document):
    character_id : int
    question : str
    answer : str