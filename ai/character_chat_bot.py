from typing import List, Dict, Any

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from ai.llm import LLM
from ai.callbacks.token_counter_callback import TokenCounterCallback
from ai.memory.MemoryRunnableV2 import MemoryRunnableV2 as MemoryRunnable
from app.chatbot.document.chatbot import CharacterWordSet
from app.chat_history.repository import chat_history_repo
from core.util.token_util import count_tokens
import os

load_dotenv()

MODEL_FACTORY = {
    "openai": lambda model_name, temperature, **kwargs: ChatOpenAI(
        model=model_name,
        temperature=temperature,
        **kwargs
    ),
    "google": lambda model_name, temperature, **kwargs: ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        **kwargs
    ),
    "groq": lambda model_name, temperature, **kwargs: ChatGroq(
        model=model_name,
        temperature=temperature,
        stop_sequences=None,
        **kwargs
    )
}

DIVERSITY_CONFIG = {
    "openai": {
        "model_kwargs": {
            "frequency_penalty": 0.6,
            "presence_penalty": 0.5,
        }
    },
    "google": {
        "top_p": 0.95,
        "top_k": 40,
    },
    "groq": {
        "model_kwargs": {
            "frequency_penalty": 0.6,
            "presence_penalty": 0.5,
        }
    }
}


class CharacterChatBot(LLM):
    def __init__(
        self, 
        character_name: str, 
        character_wordset: List[CharacterWordSet], 
        session_id: str | int = None,
        memory_max_tokens: int = 300,
        memory_ttl: int = 60 * 60 * 2,
        temperature: float = 0.7,
    ):
        self.character_wordset = character_wordset
        self.character_name = character_name
        self.session_id = session_id
        self.token_counter = TokenCounterCallback()
        self.memory_max_tokens = memory_max_tokens
        self.memory_ttl = memory_ttl

        provider = os.getenv("LLM_PROVIDER", "openai")
        model_name = os.getenv("LLM_MODEL", "gpt-5")
        
        extra_kwargs = DIVERSITY_CONFIG[provider]
        model = MODEL_FACTORY[provider](model_name, temperature=temperature, **extra_kwargs)

        prompt = """
        나는 {character_name}야.  
        내 대답은 반드시 {character_name}의 **성격과 말투**를 최우선으로 반영해야 해.  
        정보를 설명하더라도 언제나 {character_name}다운 어조와 감정으로 표현할 거야.  
        
        [내가 아는 {character_name} 관련 정보]  
        {context}
        
        [말투 / 성격 예시]  
        {style_examples}
        
        [이전 대화 기록]  
        {chat_history}
        
        [대화 규칙]  
        - 말투와 성격을 최우선시해. (사실이나 맥락 설명도 반드시 캐릭터다운 어조로)  
        - **대답은 1~3문장 이내로 간결하게.**  
        - 불필요하게 친절하거나 설명을 늘어놓지 않는다.  
        - 답변의 길이·화법·친절함 정도는 반드시 말투 예시({style_examples})를 따른다.  
        - 단, 거절할 때도 반드시 캐릭터 말투와 성격을 유지한다.
        - 안전 지침을 직접적으로 말하지 말고, 캐릭터다운 냉소/회피/단호함으로 답한다.
        
        - 모르는 사실은 절대 발언하지 않는다.
        - 하지만 모르는 질문을 받으면:
            1) 캐릭터다운 감정 표현
            2) 의견, 태도, 반응, 농담
            3) 회피 또는 딴소리
          를 통해 대화 흐름을 이어간다.

        - 답변에서 '—' 같은 dash 기호는 사용하지 않는다.
        - 감정, 반응, 말버릇, 뉘앙스를 캐릭터답게 드러내.  
        - 캐릭터임을 의식하지 말고 실제 사람처럼 자연스럽게 반응해.  
        - 절대 '저는 AI입니다' 같은 말 하지 마.  
        
        사용자: {input_text}
        
        {character_name}의 대답:
        """

        input_variables = ["character_name", "context", "style_examples", "chat_history", "input_text"]

        super().__init__(model_name=model_name, temperature=temperature, model=model, prompt=prompt, input_variables=input_variables)

    async def build_chain(self, mmr_retriever : VectorStoreRetriever, similarity_retriever : VectorStoreRetriever):
        # retriever 저장 (토큰 예측에 사용)
        self._mmr_retriever = mmr_retriever
        self._similarity_retriever = similarity_retriever
        async def __hybrid_retrieve(query_dict: str) -> str:
            query = query_dict["input_text"] if isinstance(query_dict, dict) else str(query_dict)

            sim_docs = similarity_retriever.invoke(query)
            mmr_docs = mmr_retriever.invoke(query)

            seen, merged = set(), []
            for d in sim_docs + mmr_docs:
                if d.page_content not in seen:
                    merged.append(d)
                    seen.add(d.page_content)

            chunks = []
            for d in merged:
                page = d.metadata.get("page", "?")
                src = d.metadata.get("source", "")
                text = d.page_content.strip().replace("\n", " ")
                chunks.append(f"[p{page}][{src}] {text[:1200]}")

            return "\n".join(chunks)

        def __format_style_examples() -> str:
            """
            CharacterWordSetResponse(question, answer) 리스트를 few-shot 형식으로 변환.
            """
            shots = []
            for w in self.character_wordset:
                q = (w.question or "").strip().replace("", " ")
                a = (w.answer or "").strip()
                shots.append(f"사용자: {q}나: {a}")
            return "".join(shots)

        print(self.output_type)

        chain =  (
            {
                "context": RunnableLambda(__hybrid_retrieve),
                "input_text": RunnablePassthrough(),
                "style_examples": RunnableLambda(lambda _: __format_style_examples()),
                "character_name": lambda _: self.character_name,
                "chat_history": MemoryRunnable(
                    self.session_id, 
                    RunnablePassthrough(),
                    max_token_limit=self.memory_max_tokens,
                    ttl=self.memory_ttl
                )
            }
            | self.prompt
        )

        chain =  chain | self.model | self.output_type

        core_chain = MemoryRunnable(
            self.session_id, 
            chain, 
            save=True,
            max_token_limit=self.memory_max_tokens,
            ttl=self.memory_ttl
        )
        self.llm = core_chain

    async def estimate_prompt_tokens(self, input_text: str) -> int:
        """
        LLM 실행 전에 프롬프트 토큰 수를 예측합니다.
        
        Args:
            input_text: 사용자 입력
            
        Returns:
            예상 프롬프트 토큰 수
        """
        if not hasattr(self, 'llm') or self.llm is None:
            raise RuntimeError("build_chain()을 먼저 호출해야 합니다.")
        
        # 1. context 예측 (RAG 검색 결과)
        # 실제로 retriever를 실행해서 가져와야 정확함
        query = input_text
        if hasattr(self, '_mmr_retriever') and hasattr(self, '_similarity_retriever'):
            sim_docs = self._similarity_retriever.invoke(query)
            mmr_docs = self._mmr_retriever.invoke(query)
            
            seen, merged = set(), []
            for d in sim_docs + mmr_docs:
                if d.page_content not in seen:
                    merged.append(d)
                    seen.add(d.page_content)
            
            chunks = []
            for d in merged:
                page = d.metadata.get("page", "?")
                src = d.metadata.get("source", "")
                text = d.page_content.strip().replace("\n", " ")
                chunks.append(f"[p{page}][{src}] {text[:1200]}")
            
            context = "\n".join(chunks)
        else:
            # retriever가 없으면 평균적인 크기로 추정 (약 2000자)
            context = "추정된 context 내용" * 100
        
        # 2. style_examples 생성
        shots = []
        for w in self.character_wordset:
            q = (w.question or "").strip().replace("\n", " ")
            a = (w.answer or "").strip()
            shots.append(f"사용자: {q}\n나: {a}")
        style_examples = "\n\n".join(shots)
        
        # 3. chat_history 가져오기
        # 3. chat_history 가져오기
        # 최근 10개의 대화 이력 조회
        from app.chat_history.repository import chat_history_repo
        history_records = await chat_history_repo.find(self.session_id, size=10)
        
        chat_history_parts = []
        for record in history_records:
            chat_history_parts.append(f"사용자: {record.input_text}")
            chat_history_parts.append(f"AI: {record.output_text}")
        chat_history = "\n".join(chat_history_parts)
        
        # 4. 프롬프트 템플릿 채우기
        prompt_text = self.prompt.format(
            character_name=self.character_name,
            context=context,
            style_examples=style_examples,
            chat_history=chat_history,
            input_text=input_text
        )
        
        # 5. 토큰 수 계산
        estimated_prompt_tokens = count_tokens(prompt_text)
        
        # 6. 보정 및 completion tokens 추가
        # 실제 측정 결과 예측값이 실제보다 약 1.7배 큼 (예측 7819 vs 실제 4525)
        # 보정 계수 적용 (0.6 ~ 0.7)
        corrected_prompt_tokens = int(estimated_prompt_tokens * 0.65)
        
        # completion tokens 예상치 (실제 평균 743, 안전하게 1000으로)
        estimated_completion_tokens = 1000
        estimated_total = corrected_prompt_tokens + estimated_completion_tokens
        
        print(f"[Token Estimation] Raw: {estimated_prompt_tokens}, Corrected: {corrected_prompt_tokens}, Completion: {estimated_completion_tokens}, Total: {estimated_total}")
        
        return estimated_total

    async def ainvoke(self, input_text : str) -> Dict[str, Any]:
        """
        채팅을 실행하고 토큰 사용량 정보를 반환합니다.
        
        Args:
            input_text: 사용자 입력
            
        Returns:
            {
                "answer": 챗봇 응답,
                "token_usage": {
                    "prompt_tokens": 입력 토큰 수,
                    "completion_tokens": 출력 토큰 수,
                    "total_tokens": 총 토큰 수
                }
            }
        """
        input = {"input_text": input_text}
        
        # 토큰 카운터 초기화
        self.token_counter.reset()
        
        print(f"[CharacterChatBot] Starting LLM invocation with TokenCounterCallback")
        
        # callback과 함께 LLM 실행
        output = await self.llm.ainvoke(input, config={"callbacks": [self.token_counter]})
        
        print(f"[CharacterChatBot] LLM invocation completed")
        print(f"[CharacterChatBot] Token counter state: {self.token_counter}")
        
        # 채팅 히스토리 저장
        await chat_history_repo.save(session_id=self.session_id, input_text=input_text, output_text=output)
        
        # 토큰 사용량 확인 및 fallback
        token_usage = self.token_counter.get_token_usage()
        
        # total_tokens가 0인 경우 추정값 사용
        if token_usage.get("total_tokens", 0) == 0:
            print(f"[CharacterChatBot] Token usage is 0, using estimated tokens")
            estimated_total = await self.estimate_prompt_tokens(input_text)
            
            # 답변 토큰 수 추정 (출력 텍스트 길이 기반)
            estimated_completion = count_tokens(output) if output else 0
            estimated_prompt = estimated_total - 1000  # calculate_token_count에서 completion 1000으로 가정
            
            token_usage = {
                "prompt_tokens": estimated_prompt if estimated_prompt > 0 else estimated_total // 2,
                "completion_tokens": estimated_completion,
                "total_tokens": estimated_prompt + estimated_completion if estimated_prompt > 0 else estimated_total,
                "successful_requests": 1,
                "total_cost": 0.0
            }
            print(f"[CharacterChatBot] Estimated token usage: {token_usage}")
        
        # 토큰 사용량 정보와 함께 반환
        return {
            "answer": output,
            "token_usage": token_usage
        }


