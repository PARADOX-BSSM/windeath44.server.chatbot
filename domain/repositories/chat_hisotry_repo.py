from domain.documents.chat_history import ChatHistory


async def save(session_id : str, input_text : str, output_text : str):
    chat_history = ChatHistory(session_id=session_id, input_text=input_text, output_text=output_text)
    chat_history.save()
