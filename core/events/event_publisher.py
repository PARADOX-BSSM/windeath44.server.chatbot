from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class EventPublisher(ABC):
    """
    Event Publisher 인터페이스 (Adapter 패턴의 Target Interface)
    
    다양한 메시징 시스템(Kafka, RabbitMQ, SQS 등)에 대한 공통 인터페이스를 정의합니다.
    """
    
    @abstractmethod
    async def publish(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        이벤트를 발행합니다.
        
        Args:
            topic: 메시지를 발행할 토픽/큐 이름
            message: 발행할 메시지 데이터
            key: 메시지 키 (파티셔닝에 사용)
            headers: 메시지 헤더
            
        Returns:
            bool: 발행 성공 여부
        """
        pass
    
    @abstractmethod
    async def publish_batch(
        self,
        topic: str,
        messages: list[Dict[str, Any]],
        keys: Optional[list[str]] = None
    ) -> bool:
        """
        여러 이벤트를 배치로 발행합니다.
        
        Args:
            topic: 메시지를 발행할 토픽/큐 이름
            messages: 발행할 메시지 리스트
            keys: 각 메시지에 대응하는 키 리스트
            
        Returns:
            bool: 발행 성공 여부
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        연결을 종료하고 리소스를 정리합니다.
        """
        pass
    
    @abstractmethod
    async def connect(self) -> None:
        """
        메시징 시스템에 연결합니다.
        """
        pass
