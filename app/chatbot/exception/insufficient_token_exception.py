from core.exceptions.business_exception import BusinessException


class InsufficientTokenException(BusinessException):
    """토큰이 부족할 때 발생하는 예외"""
    
    def __init__(self, required_tokens: int, remain_tokens: int):
        self.required_tokens = required_tokens
        self.remain_tokens = remain_tokens
        super().__init__(
            status_code=400,
            message=f"토큰이 부족합니다. 필요: {required_tokens}, 남은 토큰: {remain_tokens}"
        )
