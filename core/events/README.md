# Event Publisher (Adapter Pattern)

Kafka를 포함한 다양한 메시징 시스템을 위한 통합 이벤트 발행 인터페이스입니다.

## 📐 아키텍처 (Adapter Pattern)

```
┌─────────────────────────────────┐
│   EventPublisher (Interface)     │  ← Target Interface
│  - publish()                      │
│  - publish_batch()               │
│  - connect()                     │
│  - close()                       │
└─────────────────────────────────┘
           ▲
           │ implements
           │
┌──────────┴──────────────────────┐
│  KafkaEventPublisher (Adapter)   │
│  - aiokafka 라이브러리 래핑       │
│  - Kafka 특화 로직               │
└──────────────────────────────────┘
```

### Adapter 패턴의 장점

1. **유연성**: 메시징 시스템을 쉽게 교체 가능 (Kafka → RabbitMQ → SQS)
2. **테스트 용이성**: Mock 구현체를 만들어 테스트 가능
3. **일관성**: 모든 메시징 시스템에 대해 동일한 인터페이스 사용
4. **확장성**: 새로운 메시징 시스템 추가가 간단

## 📦 설치

```bash
pip install aiokafka
```

또는 requirements.txt에 추가:
```
aiokafka==0.8.1
```

## ⚙️ 설정

`.env` 파일에 Kafka 설정을 추가하세요:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CLIENT_ID=fastapi-event-publisher
KAFKA_COMPRESSION_TYPE=gzip
KAFKA_ACKS=all
```

### 설정 옵션

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka 브로커 주소 (쉼표로 구분)
- `KAFKA_CLIENT_ID`: 클라이언트 식별자
- `KAFKA_COMPRESSION_TYPE`: 압축 타입 (`gzip`, `snappy`, `lz4`, `zstd`, `none`)
- `KAFKA_ACKS`: 응답 확인 레벨
  - `0`: 응답 없음 (가장 빠름, 메시지 손실 가능)
  - `1`: 리더만 확인 (균형)
  - `all`: 모든 복제본 확인 (가장 안전, 느림)

## 🚀 사용법

### 1. FastAPI 의존성 주입 방식 (권장)

```python
from fastapi import FastAPI, Depends
from core.events.event_publisher import EventPublisher
from core.events.deps import get_event_publisher, close_event_publisher

app = FastAPI()

@app.on_event("shutdown")
async def shutdown():
    await close_event_publisher()

@app.post("/users")
async def create_user(
    publisher: EventPublisher = Depends(get_event_publisher)
):
    # 이벤트 발행
    await publisher.publish(
        topic="user-events",
        message={
            "event_type": "user_created",
            "user_id": "12345",
            "timestamp": "2025-10-16T00:00:00Z"
        },
        key="12345",
        headers={"source": "api-server"}
    )
    
    return {"status": "success"}
```

### 2. 직접 사용 방식

```python
from core.events.kafka_event_publisher import KafkaEventPublisher

async def main():
    publisher = KafkaEventPublisher(
        bootstrap_servers="localhost:9092",
        client_id="my-service"
    )
    
    try:
        await publisher.connect()
        
        # 단일 메시지 발행
        await publisher.publish(
            topic="my-topic",
            message={"key": "value"},
            key="message-key"
        )
        
        # 배치 메시지 발행
        await publisher.publish_batch(
            topic="my-topic",
            messages=[
                {"id": 1, "data": "first"},
                {"id": 2, "data": "second"}
            ],
            keys=["key1", "key2"]
        )
        
    finally:
        await publisher.close()
```

### 3. 배치 발행

```python
messages = [
    {"event": "page_view", "page": "/home"},
    {"event": "page_view", "page": "/products"},
    {"event": "page_view", "page": "/about"}
]

keys = ["user1", "user2", "user3"]

success = await publisher.publish_batch(
    topic="analytics",
    messages=messages,
    keys=keys
)
```

## 🧪 테스트용 Mock Publisher

```python
from core.events.event_publisher import EventPublisher
from typing import Dict, Any, Optional

class MockEventPublisher(EventPublisher):
    """테스트용 Mock Publisher"""
    
    def __init__(self):
        self.published_messages = []
    
    async def connect(self):
        pass
    
    async def publish(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        self.published_messages.append({
            "topic": topic,
            "message": message,
            "key": key,
            "headers": headers
        })
        return True
    
    async def publish_batch(
        self,
        topic: str,
        messages: list[Dict[str, Any]],
        keys: Optional[list[str]] = None
    ) -> bool:
        for i, msg in enumerate(messages):
            self.published_messages.append({
                "topic": topic,
                "message": msg,
                "key": keys[i] if keys else None
            })
        return True
    
    async def close(self):
        pass

# 테스트에서 사용
async def test_my_function():
    mock_publisher = MockEventPublisher()
    
    await my_function(mock_publisher)
    
    # 검증
    assert len(mock_publisher.published_messages) == 1
    assert mock_publisher.published_messages[0]["topic"] == "expected-topic"
```

## 🔌 다른 Adapter 추가하기

RabbitMQ, AWS SQS 등 다른 메시징 시스템을 추가하려면:

```python
from core.events.event_publisher import EventPublisher

class RabbitMQEventPublisher(EventPublisher):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        # RabbitMQ 설정
    
    async def connect(self):
        # RabbitMQ 연결 로직
        pass
    
    async def publish(self, topic, message, key=None, headers=None):
        # RabbitMQ 발행 로직
        pass
    
    async def publish_batch(self, topic, messages, keys=None):
        # RabbitMQ 배치 발행 로직
        pass
    
    async def close(self):
        # RabbitMQ 연결 종료 로직
        pass
```

## 📝 주요 메서드

### `publish()`
단일 메시지를 발행합니다.

**Parameters:**
- `topic` (str): 토픽/큐 이름
- `message` (Dict[str, Any]): 발행할 메시지
- `key` (Optional[str]): 파티션 키 (같은 키는 같은 파티션으로)
- `headers` (Optional[Dict[str, str]]): 메시지 헤더

**Returns:**
- `bool`: 발행 성공 여부

### `publish_batch()`
여러 메시지를 배치로 발행합니다.

**Parameters:**
- `topic` (str): 토픽/큐 이름
- `messages` (list[Dict[str, Any]]): 발행할 메시지 리스트
- `keys` (Optional[list[str]]): 각 메시지의 파티션 키 리스트

**Returns:**
- `bool`: 모든 발행 성공 여부

## 🎯 Best Practices

1. **Key 사용**: 순서 보장이 필요한 경우 동일한 key 사용
2. **Batch 사용**: 여러 메시지를 한 번에 보낼 때는 `publish_batch()` 사용
3. **Error Handling**: 발행 실패 시 재시도 로직 구현
4. **연결 관리**: FastAPI lifespan 이벤트에서 연결/종료 관리
5. **Compression**: 큰 메시지의 경우 압축 활성화 (`gzip`, `snappy`)

## 🔍 모니터링

```python
# 연결 상태 확인
if publisher.is_connected:
    print("Connected to Kafka")

# 로그 레벨 설정
import logging
logging.getLogger("aiokafka").setLevel(logging.DEBUG)
```

## ⚠️ 주의사항

1. **비동기 컨텍스트**: 모든 메서드는 `async`이므로 `await`와 함께 사용
2. **연결 관리**: 애플리케이션 종료 시 반드시 `close()` 호출
3. **에러 처리**: 네트워크 장애 등을 고려한 에러 처리 구현 권장
4. **성능**: 많은 메시지를 보낼 때는 `publish_batch()` 사용

## 📚 참고

- [aiokafka 문서](https://aiokafka.readthedocs.io/)
- [Kafka 공식 문서](https://kafka.apache.org/documentation/)
- [Adapter Pattern](https://refactoring.guru/design-patterns/adapter)
