
async def generate_chat_session_id(chatbot_id : int,  user_id : str) -> str:
    return  "chat:" + str(chatbot_id) + ":" + user_id