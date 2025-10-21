# FastAPIProject - 프로젝트 개요

## 프로젝트 목적
AI 캐릭터 챗봇 시스템을 제공하는 FastAPI 기반 백엔드 API 서비스입니다.

### 주요 기능
- **AI 캐릭터 챗봇**: LangChain, OpenAI, Pinecone을 활용한 RAG 기반 대화형 챗봇
- **챗봇 말투셋 관리**: 캐릭터별 말투와 스타일 커스터마이징
- **대화 히스토리**: 사용자와 챗봇 간의 대화 기록 관리
- **gRPC 통신**: User, Chatbot 등 다른 마이크로서비스와 통신
- **이벤트 처리**: Kafka를 통한 비동기 이벤트 발행/구독
- **웹 크롤링**: Selenium + Chromium을 활용한 웹 데이터 수집

## 기술 스택

### 백엔드 프레임워크
- **Python 3.11**
- **FastAPI 0.116**: 현대적인 Python 웹 프레임워크
- **Uvicorn**: ASGI 서버

### 데이터베이스 및 저장소
- **MongoDB** (Motor + Beanie ORM): 주 데이터베이스
- **Redis**: 캐싱
- **Pinecone**: 벡터 데이터베이스 (임베딩 저장)

### AI/ML
- **LangChain**: AI 애플리케이션 프레임워크
- **OpenAI API**: LLM
- **Google Generative AI**: 추가 AI 모델
- **DeepSeek**: 대체 LLM

### 메시징 및 통신
- **Kafka** (aiokafka): 이벤트 스트리밍
- **gRPC** (grpcio): 마이크로서비스 간 통신

### 웹 크롤링
- **Selenium**: 브라우저 자동화
- **undetected-chromedriver**: Chromium 드라이버
- **BeautifulSoup4**: HTML 파싱

### 배포
- **Docker**: 컨테이너화 (ARM64 지원)
- **포트**: 4449

## 프로젝트 구조

```
FastAPIProject/
├── main.py              # FastAPI 앱 진입점
├── requirements.txt     # Python 의존성
├── Dockerfile          # ARM64 Docker 이미지 설정
├── api/                # API 계층
│   ├── routers/       # 엔드포인트 라우터
│   │   ├── chatbot.py          # 챗봇 관련 API
│   │   ├── chatbot_wordset.py  # 말투셋 관리 API
│   │   ├── chat_history.py     # 대화 기록 API
│   │   └── dit.py              # DIT 관련 API
│   ├── schemas/       # Pydantic 스키마 (요청/응답)
│   └── depends/       # 의존성 주입
├── app/                # 비즈니스 로직 계층
│   ├── chatbot/       # 챗봇 서비스
│   ├── chatbot_wordset/  # 말투셋 서비스
│   ├── chat_history/  # 대화 기록 서비스
│   └── dit/           # DIT 서비스
├── core/              # 핵심 인프라
│   ├── db/           # 데이터베이스 설정
│   ├── exceptions/   # 커스텀 예외
│   ├── grpcs/        # gRPC 클라이언트
│   ├── events/       # 이벤트 발행/처리
│   ├── embedder/     # 임베딩 생성
│   ├── vectorstores/ # 벡터 저장소 연동
│   ├── sessions/     # 세션 관리
│   ├── loader/       # 데이터 로더
│   └── util/         # 유틸리티
├── ai/                # AI 관련
│   ├── character_chat_bot.py  # 캐릭터 챗봇 구현
│   ├── llm.py                 # LLM 래퍼
│   ├── memory/                # 대화 메모리
│   └── callbacks/             # LangChain 콜백
├── protos/            # gRPC protobuf 정의
└── avro/              # Avro 스키마
```

## 아키텍처 패턴

### 계층 구조
1. **API 계층** (`api/`): FastAPI 라우터, 스키마, 의존성 주입
2. **서비스 계층** (`app/`): 비즈니스 로직
3. **인프라 계층** (`core/`): DB, gRPC, 이벤트 등 인프라 관심사

### 설계 패턴
- **의존성 주입**: FastAPI의 Depends를 통한 DI
- **Repository 패턴**: 데이터 액세스 추상화
- **Event-Driven Architecture**: Kafka를 통한 비동기 이벤트 처리
- **Microservices**: gRPC를 통한 서비스 간 통신

## 환경 설정
- 환경 변수는 `.env` 파일로 관리
- CORS 설정: localhost:5173, 10.200.139.219:5173 허용
- MongoDB 연결은 앱 lifespan에서 관리 (init/close)
