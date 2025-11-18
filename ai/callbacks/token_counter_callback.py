import os
from typing import Any, Dict, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import os


class TokenCounterCallback(BaseCallbackHandler):

    
    def __init__(self):
        super().__init__()
        self.reset()
    
    def reset(self):
        """토큰 카운터를 초기화합니다."""
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0
        self.successful_requests: int = 0
        self.total_cost: float = 0.0
        
    def on_llm_start(
        self, 
        serialized: Dict[str, Any], 
        prompts: List[str], 
        **kwargs: Any
    ) -> None:
        """LLM 호출이 시작될 때 호출됩니다."""
        print(f"[TokenCounterCallback] on_llm_start called with {len(prompts)} prompts")
        pass

    
    def on_llm_end(
        self, 
        response: LLMResult, 
        **kwargs: Any
    ) -> None:
        """
        LLM 호출이 완료될 때 호출됩니다.
        OpenAI, Google Gemini, Groq 등 다양한 provider 지원
        
        Args:
            response: LLM 응답 결과 (토큰 사용량 정보 포함)
        """
        token_usage = {}
        provider = os.getenv("LLM_PROVIDER", "openai")
        
        if provider == "google":
            # Google Gemini API: usage_metadata 사용
            if response.llm_output and "usage_metadata" in response.llm_output:
                usage_metadata = response.llm_output.get("usage_metadata", {})
                token_usage = {
                    "prompt_tokens": usage_metadata.get("prompt_token_count", 0),
                    "completion_tokens": usage_metadata.get("candidates_token_count", 0),
                    "total_tokens": usage_metadata.get("total_token_count", 0)
                }
        elif provider == "openai":
            # OpenAI API: token_usage 사용
            if response.llm_output and "token_usage" in response.llm_output:
                token_usage = response.llm_output.get("token_usage", {})
        elif provider == "groq":
            # Groq API: token_usage 사용 (OpenAI 호환)
            if response.llm_output and "token_usage" in response.llm_output:
                token_usage = response.llm_output.get("token_usage", {})

            # Groq가 generation_info에 저장하는 경우도 확인
            elif response.generations:
                for generation_list in response.generations:
                    for generation in generation_list:
                        if hasattr(generation, 'generation_info') and generation.generation_info:
                            gen_token_usage = generation.generation_info.get("token_usage", {})
                            if gen_token_usage:
                                token_usage = gen_token_usage
                                break
                    if token_usage:
                        break
        
        # 토큰 정보 검증 및 경고
        if not token_usage or token_usage.get("total_tokens", 0) == 0:
            print(f"[TokenCounterCallback] WARNING: No token usage found in response")
            print(f"  Provider: {provider}")
            print(f"  llm_output keys: {list(response.llm_output.keys()) if response.llm_output else 'None'}")
            print(f"  generations count: {len(response.generations) if response.generations else 0}")
            if response.generations and len(response.generations) > 0:
                first_gen = response.generations[0][0] if response.generations[0] else None
                if first_gen and hasattr(first_gen, 'generation_info'):
                    print(f"  first generation_info keys: {list(first_gen.generation_info.keys()) if first_gen.generation_info else 'None'}")
            return
        
        # 토큰 사용량 누적
        print(f"[TokenCounterCallback] Provider: {provider}")
        print(f"[TokenCounterCallback] Token usage found: {token_usage}")
        self.prompt_tokens += token_usage.get("prompt_tokens", 0)
        self.completion_tokens += token_usage.get("completion_tokens", 0)
        self.total_tokens += token_usage.get("total_tokens", 0)
        self.successful_requests += 1
        
        # 비용 계산 (선택적)
        if response.llm_output:
            model_name = response.llm_output.get("model_name", "")
            if model_name:
                self.total_cost += self._calculate_cost(
                    model_name,
                    self.prompt_tokens,
                    self.completion_tokens
                )

    def on_llm_error(
        self, 
        error: Exception, 
        **kwargs: Any
    ) -> None:
        """LLM 호출 중 에러가 발생했을 때 호출됩니다."""
        pass
    
    def _calculate_cost(
        self, 
        model_name: str, 
        prompt_tokens: int, 
        completion_tokens: int
    ) -> float:
        """
        모델별 토큰 비용을 계산합니다.

        Args:
            model_name: 모델 이름
            prompt_tokens: 입력 토큰 수
            completion_tokens: 출력 토큰 수
            
        Returns:
            총 비용 (USD)
        """
        # OpenAI 가격표 (2025년 기준, 실제 가격은 공식 문서 확인 필요)
        pricing = {
            "gpt-4": {
                "prompt": 0.03 / 1000,  # $0.03 per 1K tokens
                "completion": 0.06 / 1000  # $0.06 per 1K tokens
            },
            "gpt-4-turbo": {
                "prompt": 0.01 / 1000,
                "completion": 0.03 / 1000
            },
            "gpt-3.5-turbo": {
                "prompt": 0.0005 / 1000,
                "completion": 0.0015 / 1000
            },
            "gpt-5": {  # 예시 (실제 가격 확인 필요)
                "prompt": 0.05 / 1000,
                "completion": 0.10 / 1000
            }
        }
        
        # 모델 이름에서 기본 모델 추출 (gpt-4-0613 -> gpt-4)
        base_model = None
        for model_key in pricing.keys():
            if model_name.startswith(model_key):
                base_model = model_key
                break
        
        if base_model is None:
            return 0.0
        
        prompt_cost = prompt_tokens * pricing[base_model]["prompt"]
        completion_cost = completion_tokens * pricing[base_model]["completion"]
        
        return prompt_cost + completion_cost
    
    def get_token_usage(self) -> Dict[str, int]:
        """
        현재까지의 토큰 사용량을 반환합니다.
        
        Returns:
            토큰 사용량 딕셔너리
        """
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "successful_requests": self.successful_requests,
            "total_cost": round(self.total_cost, 6)
        }
    
    def __repr__(self) -> str:
        return (
            f"TokenCounterCallback("
            f"prompt_tokens={self.prompt_tokens}, "
            f"completion_tokens={self.completion_tokens}, "
            f"total_tokens={self.total_tokens}, "
            f"requests={self.successful_requests})"
        )
