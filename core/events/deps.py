from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings

from core.events.event_publisher import EventPublisher
from core.events.kafka_event_publisher import KafkaEventPublisher


class KafkaSettings(BaseSettings):
    """Kafka 설정"""
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_client_id: str = "fastapi-event-publisher"
    kafka_compression_type: str = "gzip"
    kafka_acks: str = "all"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # .env 파일의 다른 필드들 무시


@lru_cache()
def get_kafka_settings() -> KafkaSettings:
    """Kafka 설정을 반환합니다."""
    return KafkaSettings()


# 전역 프로듀서 인스턴스 (싱글톤 패턴)
_kafka_publisher: Optional[KafkaEventPublisher] = None


async def get_event_publisher() -> EventPublisher:
    """
    FastAPI dependency로 사용할 Event Publisher를 반환합니다.
    
    Usage:
        @app.post("/example")
        async def example(publisher: EventPublisher = Depends(get_event_publisher)):
            await publisher.publish("my-topic", {"key": "value"})
    """
    global _kafka_publisher
    
    if _kafka_publisher is None:
        settings = get_kafka_settings()
        _kafka_publisher = KafkaEventPublisher(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            client_id=settings.kafka_client_id,
            compression_type=settings.kafka_compression_type,
            acks=settings.kafka_acks
        )
        await _kafka_publisher.connect()
    
    return _kafka_publisher


async def close_event_publisher() -> None:
    """애플리케이션 종료 시 Event Publisher 연결을 종료합니다."""
    global _kafka_publisher
    
    if _kafka_publisher is not None:
        await _kafka_publisher.close()
        _kafka_publisher = None
