"""
XSS 방어를 위한 전역 sanitizing이 적용된 Base Model
"""
from typing import Any
from pydantic import BaseModel, model_validator

from core.util.xss_util import sanitize


class XSSBaseModel(BaseModel):
    """
    모든 문자열 필드를 자동으로 sanitize하는 Base Model
    
    Spring Boot의 Jackson Module 등록과 유사한 방식으로,
    모든 DTO가 이 클래스를 상속받으면 전역적으로 XSS 방어가 적용됩니다.
    
    Example:
        ```python
        class UserCreateRequest(XSSBaseModel):
            userId: str
            nickname: str
        
        # 사용 시 자동으로 sanitize 적용됨
        request = UserCreateRequest(
            userId="<script>alert('xss')</script>",
            nickname="홍길동"
        )
        # request.userId = "&lt;script&gt;alert('xss')&lt;/script&gt;"
        ```
    """
    
    @model_validator(mode="after")
    def sanitize_strings(self) -> "XSSBaseModel":
        """
        모든 문자열 필드를 자동으로 sanitize합니다.
        
        - 중첩된 객체의 문자열도 재귀적으로 처리
        - List, Dict 내부의 문자열도 처리
        """
        self._sanitize_field_recursive(self.__dict__)
        return self
    
    def _sanitize_field_recursive(self, data: Any) -> Any:
        """
        재귀적으로 데이터 구조를 순회하며 문자열을 sanitize합니다.
        
        Args:
            data: sanitize할 데이터 (dict, list, str 등)
            
        Returns:
            sanitize된 데이터
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = sanitize(value)
                elif isinstance(value, (dict, list)):
                    self._sanitize_field_recursive(value)
                elif isinstance(value, BaseModel):
                    # 중첩된 Pydantic 모델 처리
                    self._sanitize_field_recursive(value.__dict__)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    data[i] = sanitize(item)
                elif isinstance(item, (dict, list)):
                    self._sanitize_field_recursive(item)
                elif isinstance(item, BaseModel):
                    # 중첩된 Pydantic 모델 처리
                    self._sanitize_field_recursive(item.__dict__)
        
        return data
