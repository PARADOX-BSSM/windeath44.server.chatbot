from exceptions.business_exception import BusinessException


class CharacterWordSetLengthExceededException(BusinessException):
    def __init__(self, length : int):
        message = f"말투셋 크기가 최대 크기인 {length}보다 큽니다.."
        status_code = 400
        super().__init__(message=message, status_code=status_code)