from core.exceptions.business_exception import BusinessException


class NotFoundChatBotException(BusinessException):
    def __init__(self, chatbot_id : int):
        message = f"챗봇 {chatbot_id}를 찾지 못하였습니다."
        status_code = 404
        super().__init__(message=message, status_code=status_code)