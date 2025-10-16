import time
import uuid
from typing import Dict, Any, Optional

from core.events.event_publisher import EventPublisher


async def publish_chat_event(
    publisher: EventPublisher,
    chatbot_id: int,
    user_id: str,
    session_id: str,
    content: str,
    answer: str,
    token_usage: Dict[str, Any],
    success: bool = True,
    error_message: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    model_name: str = "gpt-5"
) -> bool:
    """
    챗봇 채팅 이벤트를 Kafka에 발행합니다.
    
    Args:
        publisher: EventPublisher 인스턴스
        chatbot_id: 챗봇 ID
        user_id: 사용자 ID
        session_id: 세션 ID
        content: 사용자 입력
        answer: 챗봇 응답
        token_usage: 토큰 사용량 정보
        success: 성공 여부
        error_message: 에러 메시지 (실패 시)
        response_time_ms: 응답 시간 (밀리초)
        model_name: 사용된 LLM 모델 이름
        
    Returns:
        bool: 발행 성공 여부
    """
    
    # 이벤트 데이터 구성 (avro 스키마에 맞춤)
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "chat_completed" if success else "chat_failed",
        "timestamp": int(time.time() * 1000),  # milliseconds
        "chatbot_id": chatbot_id,
        "user_id": user_id,
        "session_id": session_id,
        "content": content,
        "answer": answer if success else None,
        "content_token_count": token_usage.get("prompt_tokens", 0),
        "answer_token_count": token_usage.get("completion_tokens", 0) if success else None,
        "total_token_count": token_usage.get("total_tokens", 0),
        "retriever_used": True,
        "retriever_docs_count": None,  # TODO: retriever에서 가져온 문서 수 추가
        "success": success,
        "error_message": error_message,
        "response_time_ms": response_time_ms,
        "model_name": model_name,
        "metadata": None
    }
    
    # Kafka 토픽에 발행
    topic = "chatbot-chat-events"
    key = f"{chatbot_id}:{user_id}"  # 같은 사용자의 채팅은 같은 파티션으로
    
    return await publisher.publish(
        topic=topic,
        message=event,
        key=key,
        headers={"event_type": event["event_type"]}
    )
