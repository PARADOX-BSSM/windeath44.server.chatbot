import tiktoken
from typing import Optional


class TokenUtil:
    DEFAULT_ENCODING = "cl100k_base"
    
    def __init__(self, encoding_name: str = DEFAULT_ENCODING):
        """
            encoding_name: tiktoken 인코딩 이름 (기본값: "cl100k_base")
                          - "cl100k_base": gpt-4, gpt-3.5-turbo, text-embedding-ada-002
                          - "p50k_base": Codex models, text-davinci-002, text-davinci-003
                          - "r50k_base": GPT-3 models like davinci
        """
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def count_tokens_batch(self, texts: list[str]) -> list[int]:
        return [self.count_tokens(text) for text in texts]
    
    def is_within_limit(self, text: str, limit: int) -> bool:
        return self.count_tokens(text) <= limit
    
    @classmethod
    def count_tokens_for_model(cls, text: str, model: str) -> int:

        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding(cls.DEFAULT_ENCODING)
        
        if not text:
            return 0
        return len(encoding.encode(text))


_default_token_util: Optional[TokenUtil] = None


def get_token_util() -> TokenUtil:
    global _default_token_util
    if _default_token_util is None:
        _default_token_util = TokenUtil()
    return _default_token_util


# 편의 함수들
def count_tokens(text: str) -> int:
    """
    텍스트의 토큰 수를 계산 (편의 함수)
    
    Args:
        text: 토큰을 계산할 텍스트
        
    Returns:
        토큰 수
    """
    return get_token_util().count_tokens(text)


def is_within_token_limit(text: str, limit: int) -> bool:
    """
    텍스트의 토큰 수가 제한 내에 있는지 확인 (편의 함수)
    
    Args:
        text: 확인할 텍스트
        limit: 토큰 제한 수
        
    Returns:
        제한 내에 있으면 True, 초과하면 False
    """
    return get_token_util().is_within_limit(text, limit)
