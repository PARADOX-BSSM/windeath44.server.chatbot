from exceptions.business_exception import BusinessException


class AlreadyExistsChatbotException(BusinessException):
    def __init__(self, character_id : int):
        message = f"{character_id}의 챗봇이 이미 존재합니다."
        status_code = 400
        super().__init__(message=message, status_code=status_code)