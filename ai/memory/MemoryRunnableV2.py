"""
새 LangChain 생태계(1.0+) 호환 Memory Runnable.
기존 MemoryRunnable의 동작을 유지하면서 새 API를 사용합니다.
"""
import os
from typing import Dict, Any, Optional, List
from langchain_core.runnables import Runnable
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class InMemorySummarizer:
    """
    ConversationSummaryBufferMemory를 대체하는 간단한 요약 메커니즘.
    Redis에 저장된 메시지가 max_token_limit를 초과하면 요약을 생성합니다.
    """
    
    def __init__(
        self,
        chat_history: BaseChatMessageHistory,
        llm: Any,
        max_token_limit: int = 500,
    ):
        self.chat_history = chat_history
        self.llm = llm
        self.max_token_limit = max_token_limit
    
    def _estimate_tokens(self, messages: List[BaseMessage]) -> int:
        """메시지 토큰 수 추정 (대략 4 chars = 1 token)"""
        total_chars = sum(len(msg.content) for msg in messages)
        return total_chars // 4
    
    def _summarize_messages(self, messages: List[BaseMessage]) -> str:
        """메시지 리스트를 요약"""
        conversation = "\n".join(
            f"{'사용자' if isinstance(m, HumanMessage) else 'AI'}: {m.content}"
            for m in messages
        )
        
        summary_prompt = f"""다음 대화를 간결하게 요약해주세요:

{conversation}

요약:"""
        
        response = self.llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content
    
    def load_memory_variables(self) -> Dict[str, Any]:
        """메모리 로드 (요약 포함)"""
        messages = self.chat_history.messages
        
        if not messages:
            return {"chat_history": []}
        
        # 토큰 수 체크
        estimated_tokens = self._estimate_tokens(messages)
        
        if estimated_tokens > self.max_token_limit:
            # 요약 생성 (최근 메시지는 유지)
            summary_text = self._summarize_messages(messages[:-4])  # 마지막 4개 제외하고 요약
            recent_messages = messages[-4:]
            
            # 요약을 시스템 메시지로 변환
            from langchain_core.messages import SystemMessage
            summary_msg = SystemMessage(content=f"이전 대화 요약: {summary_text}")
            
            return {"chat_history": [summary_msg] + recent_messages}
        
        return {"chat_history": messages}
    
    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]) -> None:
        """대화 저장"""
        input_key = list(inputs.keys())[0]
        output_key = list(outputs.keys())[0]
        
        self.chat_history.add_user_message(inputs[input_key])
        self.chat_history.add_ai_message(outputs[output_key])


class MemoryRunnableV2(Runnable):
    """
    새 LangChain 생태계 호환 Memory Runnable.
    기존 MemoryRunnable과 동일한 인터페이스를 유지합니다.
    """
    
    def __init__(
        self,
        session_id: str,
        runnable: Runnable,
        save: bool = False,
        max_token_limit: int = 500,
        ttl: int = 60 * 60 * 24,
    ):
        self.runnable = runnable
        self.memory = None
        self.save = save
        self.session_id = session_id
        self.ttl = ttl
        
        if session_id:
            # Redis 채팅 히스토리
            chat_history = RedisChatMessageHistory(
                session_id=str(session_id),
                url=os.getenv("REDIS_URL", "redis://localhost:6379"),
                ttl=ttl,
            )
            
            # 요약용 LLM (gpt-3.5-turbo)
            summary_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            
            # 커스텀 요약 메모리
            self.memory = InMemorySummarizer(
                chat_history=chat_history,
                llm=summary_llm,
                max_token_limit=max_token_limit,
            )
    
    def _format_chat_history(self, messages: List[BaseMessage]) -> str:
        """메시지 리스트를 문자열로 포맷팅"""
        if not messages:
            return ""
        
        formatted = []
        for m in messages:
            if isinstance(m, HumanMessage):
                formatted.append(f"사용자: {m.content}")
            elif isinstance(m, AIMessage):
                formatted.append(f"나: {m.content}")
            else:
                # SystemMessage 등
                formatted.append(f"{m.type}: {m.content}")
        
        return "\n".join(formatted)
    
    def invoke(self, input_dict: Dict[str, Any], config=None) -> str:
        """동기 실행"""
        chat_history = ""
        if self.memory:
            raw_history = self.memory.load_memory_variables()["chat_history"]
            if raw_history:
                chat_history = (
                    self._format_chat_history(raw_history)
                    if isinstance(raw_history, list)
                    else raw_history
                )
        
        merged_input = {**input_dict, "chat_history": str(chat_history)}
        output = self.runnable.invoke(merged_input, config)
        
        if self.memory and self.save:
            self.memory.save_context(
                {"input_text": merged_input.get("input_text", merged_input.get("input", ""))},
                {"output_text": output}
            )
        
        return output
    
    async def ainvoke(self, input_dict: Dict[str, Any], config=None) -> str:
        """비동기 실행"""
        chat_history = ""
        if self.memory:
            raw_history = self.memory.load_memory_variables()["chat_history"]
            if raw_history:
                chat_history = (
                    self._format_chat_history(raw_history)
                    if isinstance(raw_history, list)
                    else raw_history
                )
        
        merged_input = {**input_dict, "chat_history": str(chat_history)}
        output = await self.runnable.ainvoke(merged_input, config)
        
        if self.memory and self.save:
            self.memory.save_context(
                {"input_text": merged_input.get("input_text", merged_input.get("input", ""))},
                {"output_text": output}
            )
        
        return output
