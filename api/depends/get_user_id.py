from fastapi import Header

async def get_user_id(user_id: str = Header(alias="user-chatbot_id")):
    return user_id
