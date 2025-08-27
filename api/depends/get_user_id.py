from fastapi import Header

async def get_user_id(user_id: str = Header(alias="user-id")):
    return user_id
