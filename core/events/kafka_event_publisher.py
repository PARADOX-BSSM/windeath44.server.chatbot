import asyncio
import json
import logging
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from core.events.event_publisher import EventPublisher


logger = logging.getLogger(__name__)


class KafkaEventPublisher(EventPublisher):
    """
    Kafka Event Publisher 구현체 (Adapter 패턴의 Adapter)

    """
    
    def __init__(
        self,
        bootstrap_servers: str | list[str],
        client_id: Optional[str] = None,
        compression_type: Optional[str] = "gzip",
        max_batch_size: int = 16384,
        linger_ms: int = 10,
        acks: str | int = "all",
        **kwargs
    ):
        """
        Kafka Event Publisher를 초기화합니다.
        
        Args:
            bootstrap_servers: Kafka 브로커 주소 (문자열 또는 리스트)
            client_id: 클라이언트 식별자
            compression_type: 압축 타입 (gzip, snappy, lz4, zstd)
            max_batch_size: 배치 최대 크기 (bytes)
            linger_ms: 배치를 보내기 전 대기 시간 (ms)
            acks: 응답 확인 레벨 (0, 1, 'all')
            **kwargs: 추가 AIOKafkaProducer 설정
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id or "kafka-event-publisher"
        self.compression_type = compression_type
        self.max_batch_size = max_batch_size
        self.linger_ms = linger_ms
        self.acks = acks
        self.extra_config = kwargs
        
        self._producer: Optional[AIOKafkaProducer] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Kafka 프로듀서를 생성하고 연결합니다."""
        if self._connected:
            logger.warning("Already connected to Kafka")
            return
        
        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                compression_type=self.compression_type,
                max_batch_size=self.max_batch_size,
                linger_ms=self.linger_ms,
                acks=self.acks,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                **self.extra_config
            )
            await self._producer.start()
            self._connected = True
            logger.info(f"Connected to Kafka: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    async def publish(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        단일 이벤트를 Kafka 토픽에 발행합니다.
        
        Args:
            topic: Kafka 토픽 이름
            message: 발행할 메시지 딕셔너리
            key: 파티션 키 (같은 키는 같은 파티션으로)
            headers: 메시지 헤더
            
        Returns:
            bool: 발행 성공 여부
        """
        if not self._connected or self._producer is None:
            logger.error("Producer is not connected. Call connect() first.")
            return False
        
        try:
            key_bytes = key.encode('utf-8') if key else None
            headers_list = [(k, v.encode('utf-8')) for k, v in headers.items()] if headers else None
            
            # 메시지 전송
            result = await self._producer.send_and_wait(
                topic=topic,
                value=message,
                key=key_bytes,
                headers=headers_list
            )
            
            logger.debug(
                f"Message sent to topic '{topic}' "
                f"[partition: {result.partition}, offset: {result.offset}]"
            )
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error while publishing message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while publishing message: {e}")
            return False
    
    async def publish_batch(
        self,
        topic: str,
        messages: list[Dict[str, Any]],
        keys: Optional[list[str]] = None
    ) -> bool:
        """
        여러 이벤트를 배치로 Kafka 토픽에 발행합니다.
        
        Args:
            topic: Kafka 토픽 이름
            messages: 발행할 메시지 리스트
            keys: 각 메시지에 대응하는 키 리스트
            
        Returns:
            bool: 모든 발행 성공 여부
        """
        if not self._connected or self._producer is None:
            logger.error("Producer is not connected. Call connect() first.")
            return False
        
        if keys and len(keys) != len(messages):
            logger.error("Keys list length must match messages list length")
            return False
        
        try:
            # 배치로 메시지 전송
            futures = []
            for idx, message in enumerate(messages):
                key = keys[idx] if keys else None
                key_bytes = key.encode('utf-8') if key else None
                
                future = await self._producer.send(
                    topic=topic,
                    value=message,
                    key=key_bytes
                )
                futures.append(future)
            
            # 모든 전송 완료 대기
            results = await asyncio.gather(*futures, return_exceptions=True)
            
            # 결과 확인
            failed = sum(1 for r in results if isinstance(r, Exception))
            if failed > 0:
                logger.warning(f"Failed to send {failed}/{len(messages)} messages")
                return False
            
            logger.info(f"Successfully sent {len(messages)} messages to topic '{topic}'")
            return True
            
        except Exception as e:
            logger.error(f"Error while publishing batch messages: {e}")
            return False
    
    async def close(self) -> None:
        """Kafka 프로듀서 연결을 종료합니다."""
        if self._producer and self._connected:
            try:
                await self._producer.stop()
                self._connected = False
                logger.info("Kafka producer connection closed")
            except Exception as e:
                logger.error(f"Error while closing Kafka producer: {e}")
        else:
            logger.warning("Producer is not connected")
    
    @property
    def is_connected(self) -> bool:
        """연결 상태를 반환합니다."""
        return self._connected
