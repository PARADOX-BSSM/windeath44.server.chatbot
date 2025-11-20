"""
XSS 방어를 위한 문자열 sanitization 유틸리티
"""
import html
import re


def sanitize(value: str) -> str:
    """
    문자열에서 XSS 공격 가능성이 있는 요소를 제거합니다.
    
    Args:
        value: sanitize할 문자열
        
    Returns:
        sanitize된 문자열
    """
    if not isinstance(value, str):
        return value
    
    # 1. HTML 엔티티 인코딩
    sanitized = html.escape(value)
    
    # 2. 스크립트 태그 제거 (대소문자 무시)
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # 3. 이벤트 핸들러 제거 (onclick, onerror 등)
    sanitized = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'\s*on\w+\s*=\s*[^\s>]*', '', sanitized, flags=re.IGNORECASE)
    
    # 4. javascript: 프로토콜 제거
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    
    # 5. data: 프로토콜 제거 (base64 인코딩된 스크립트 방지)
    sanitized = re.sub(r'data:text/html', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized
