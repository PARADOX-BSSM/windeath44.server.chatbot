from core.exceptions.business_exception import BusinessException


class AlreadyApprovedWordSetException(BusinessException):
    def __init__(self, wordset_id: str):
        message = f"말투셋 ID {wordset_id}는 이미 승인되었습니다."
        status_code = 400
        super().__init__(message=message, status_code=status_code)
