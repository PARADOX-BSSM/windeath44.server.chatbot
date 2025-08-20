from exception.business_exception import BaseException


class NotNamuwikiException(BaseException):
    def __init__(self):
        """인자를 받지 않습니다."""
        message = "URL이 나무위키 형식이 아닙니다."
        status_code = 500
        super().__init__(message=message, status_code=status_code)