# 코드 스타일 및 규칙

## 네이밍 규칙
- **변수/함수/메서드**: `snake_case`
- **클래스**: `PascalCase`
- **상수**: `UPPER_SNAKE_CASE`
- **비공개 메서드/속성**: `_leading_underscore`

## 타입 힌트
- **필수**: 모든 함수 파라미터와 반환값에 타입 힌트 사용
- **형식**: 콜론 앞에 공백 (예: `user_id : str`, `chatbot_id: int`)
  - 일관성은 없지만 대부분 콜론 뒤에만 공백
- **타입**: Python 표준 타입 힌트 사용 (`str`, `int`, `dict`, `list` 등)
- **Optional**: `Optional[T]` 또는 `T | None` 사용

## 비동기 프로그래밍
- **async/await**: FastAPI 엔드포인트와 서비스 로직에서 일관되게 사용
- **비동기 함수**: 모든 I/O 작업 (DB, API 호출, gRPC 등)은 비동기로 처리
```python
async def chat(chatbot_id: int, ...) -> BaseResponse:
    chatbot_response = await chatbot_service.chat(...)
    return BaseResponse(...)
```

## FastAPI 패턴

### 라우터
- **APIRouter 사용**: 각 도메인별로 라우터 분리
- **prefix와 tags**: 라우터 그룹화
```python
router = APIRouter(prefix="/chatbots", tags=["chatbot"])
```

### 의존성 주입
- **Depends**: FastAPI의 의존성 주입 시스템 활용
```python
async def chat(
    chatbot_id: int,
    user_id: str = Depends(get_user_id),
    user_grpc_client: UserGrpcClient = Depends(user_stub_dep),
):
    ...
```

### 응답 형식
- **BaseResponse**: 일관된 응답 래퍼 사용
```python
return BaseResponse(message="success message", data=response_data)
```

## 예외 처리
- **BusinessException**: 비즈니스 로직 예외는 커스텀 예외 사용
```python
class BusinessException(Exception):
    def __init__(self, message: str = "에러 발생", status_code: int = 500):
        self.status_code = status_code
        self.message = message
```
- **Global Exception Handler**: `main.py`에서 전역 예외 처리

## 코멘트 및 문서화
- **한글 코멘트**: 코드 내 주석은 한글로 작성
```python
# 캐릭터 챗
@router.post("/chat/{chatbot_id}")
async def chat(...):
    ...
```
- **Docstring**: 복잡한 함수에는 docstring 추가 권장 (하지만 필수는 아님)

## Import 순서
1. 표준 라이브러리
2. 서드파티 라이브러리
3. 로컬 모듈
   - `core.*`
   - `api.*`
   - `app.*`

예시:
```python
from fastapi import APIRouter, Depends, Query

from core.grpcs.client import UserGrpcClient
from api.depends.get_user_id import get_user_id
from api.schemas.request.chatbot_request import ChatRequest
from app.chatbot.service import chatbot_service
```

## 파일 구조
- **라우터**: `api/routers/` - FastAPI 엔드포인트만 정의
- **서비스**: `app/{domain}/service.py` - 비즈니스 로직
- **스키마**: `api/schemas/` - Pydantic 모델
- **의존성**: `api/depends/`, `core/*/deps/` - 의존성 주입 함수

## 데이터베이스
- **Beanie ORM**: MongoDB 모델 정의
- **MongoDB 연결**: 앱 lifespan에서 초기화/종료
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongodb(app)
    yield
    await close_mongodb(app)
```

## 코드 포맷팅
- 명시적인 린터/포맷터 설정 파일 없음
- 일반적인 Python 컨벤션 따름 (PEP 8 기반)
- 들여쓰기: 4 스페이스
