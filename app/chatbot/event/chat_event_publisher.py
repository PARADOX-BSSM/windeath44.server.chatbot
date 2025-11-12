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

    # 이벤트 데이터 구성 (avro 스키마에 정확히 맞춤)
    event = {
        "chatbot_id": chatbot_id,
        "user_id": user_id,
        "session_id": session_id,
        "content": content,
        "answer": answer if success else None,
        "content_token_count": token_usage.get("prompt_tokens", 0),
        "answer_token_count": token_usage.get("completion_tokens", 0) if success else None,
        "total_token_count": token_usage.get("total_tokens", 0),
        "success": success,
        "error_message": error_message,
        "response_time_ms": response_time_ms,
        "model_name": model_name
    }
    
    # Kafka 토픽에 발행
    topic = "chatbot-chat-request"
    key = f"{chatbot_id}:{user_id}"  # 같은 사용자의 채팅은 같은 파티션으로
    
    return await publisher.publish(
        topic=topic,
        message=event,
        key=key,

    )
