from core.exceptions.business_exception import BusinessException


class NoContentFoundException(BusinessException):
    def __init__(self, character_name: str):
        message = f"'{character_name}' 캐릭터에 대한 나무위키 콘텐츠를 찾을 수 없습니다. 챗봇 생성을 위한 소스 자료가 필요합니다."
        status_code = 404
        super().__init__(message=message, status_code=status_code)
