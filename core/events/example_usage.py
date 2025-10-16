"""
Kafka Event Publisher 사용 예시

이 파일은 Adapter 패턴을 적용한 Event Publisher의 사용법을 보여줍니다.
"""

from fastapi import FastAPI, Depends
from core.events.event_publisher import EventPublisher
from core.events.deps import get_event_publisher, close_event_publisher


# FastAPI 애플리케이션 예시
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 이벤트 퍼블리셔 초기화"""
    # get_event_publisher()를 호출하면 자동으로 연결됩니다
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 이벤트 퍼블리셔 정리"""
    await close_event_publisher()


@app.post("/example/publish")
async def publish_example(
    publisher: EventPublisher = Depends(get_event_publisher)
):
    """
    단일 이벤트 발행 예시
    """
    message = {
        "event_type": "user_registered",
        "user_id": "12345",
        "timestamp": "2025-10-16T00:00:00Z",
        "data": {
            "email": "user@example.com",
            "name": "홍길동"
        }
    }
    
    success = await publisher.publish(
        topic="user-events",
        message=message,
        key="12345",  # user_id를 키로 사용하여 순서 보장
        headers={"source": "api-server", "version": "v1"}
    )
    
    if success:
        return {"status": "success", "message": "Event published"}
    else:
        return {"status": "error", "message": "Failed to publish event"}


@app.post("/example/publish-batch")
async def publish_batch_example(
    publisher: EventPublisher = Depends(get_event_publisher)
):
    """
    배치 이벤트 발행 예시
    """
    messages = [
        {
            "event_type": "page_view",
            "user_id": "user1",
            "page": "/home",
            "timestamp": "2025-10-16T10:00:00Z"
        },
        {
            "event_type": "page_view",
            "user_id": "user2",
            "page": "/products",
            "timestamp": "2025-10-16T10:00:01Z"
        },
        {
            "event_type": "page_view",
            "user_id": "user3",
            "page": "/about",
            "timestamp": "2025-10-16T10:00:02Z"
        }
    ]
    
    keys = ["user1", "user2", "user3"]
    
    success = await publisher.publish_batch(
        topic="analytics-events",
        messages=messages,
        keys=keys
    )
    
    if success:
        return {
            "status": "success",
            "message": f"{len(messages)} events published"
        }
    else:
        return {"status": "error", "message": "Failed to publish batch events"}


# 직접 사용 예시 (의존성 주입 없이)
async def direct_usage_example():
    """
    의존성 주입 없이 직접 사용하는 예시
    """
    from core.events.kafka_event_publisher import KafkaEventPublisher
    
    # 프로듀서 생성
    publisher = KafkaEventPublisher(
        bootstrap_servers="localhost:9092",
        client_id="my-service",
        compression_type="gzip",
        acks="all"
    )
    
    try:
        # 연결
        await publisher.connect()
        
        # 메시지 발행
        success = await publisher.publish(
            topic="my-topic",
            message={"key": "value"},
            key="message-key"
        )
        
        if success:
            print("Message published successfully")
        else:
            print("Failed to publish message")
            
    finally:
        # 연결 종료
        await publisher.close()


# 다른 Adapter 구현 예시 (예: RabbitMQ)
"""
from core.events.event_publisher import EventPublisher

class RabbitMQEventPublisher(EventPublisher):
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        # ... RabbitMQ 설정
    
    async def connect(self) -> None:
        # RabbitMQ 연결 로직
        pass
    
    async def publish(self, topic: str, message: Dict[str, Any], ...) -> bool:
        # RabbitMQ로 메시지 발행 로직
        pass
    
    async def publish_batch(self, topic: str, messages: list[Dict[str, Any]], ...) -> bool:
        # RabbitMQ 배치 발행 로직
        pass
    
    async def close(self) -> None:
        # RabbitMQ 연결 종료 로직
        pass
"""
