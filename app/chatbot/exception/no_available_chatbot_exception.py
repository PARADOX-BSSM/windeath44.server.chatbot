from core.exceptions.business_exception import BusinessException


class NoAvailableChatbotException(BusinessException):
    def __init__(self):
        message = "no available chatbots."
        status_code = 404
        super().__init__(message=message, status_code=status_code)
