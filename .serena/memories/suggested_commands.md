# Suggested Commands

## 개발 환경 설정

### 가상환경 생성 및 활성화
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
```

### 의존성 설치
```bash
pip install -r requirements.txt
```

## 실행 명령어

### 로컬 개발 서버 실행
```bash
# 방법 1: uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 4449

# 방법 2: 리로드 모드 (개발용)
uvicorn main:app --host 0.0.0.0 --port 4449 --reload

# 방법 3: Python으로 직접 실행
python main.py
```

### 서버 접속
- 로컬: http://localhost:4449
- API 문서: http://localhost:4449/docs (Swagger UI)
- ReDoc: http://localhost:4449/redoc

## Docker 명령어

### Docker 이미지 빌드
```bash
# ARM64용 빌드
docker build -t fastapi-project .

# 플랫폼 명시적 지정
docker build --platform linux/arm64 -t fastapi-project .
```

### Docker 컨테이너 실행
```bash
# 기본 실행
docker run -p 4449:4449 fastapi-project

# 환경 변수 포함
docker run -p 4449:4449 --env-file .env fastapi-project

# 백그라운드 실행
docker run -d -p 4449:4449 --name fastapi-app fastapi-project
```

## 테스트

### pytest 실행
```bash
# 모든 테스트 실행
pytest

# 특정 파일 테스트
pytest tests/test_chatbot.py

# 비동기 테스트 (pytest-asyncio 사용)
pytest -v

# 벤치마크 테스트
pytest --benchmark-only
```

## Git 명령어

### 브랜치 관리
```bash
# 현재 브랜치 확인
git branch

# 상태 확인
git status

# 메인 브랜치로 전환
git checkout master

# 새 브랜치 생성 및 전환
git checkout -b feature/new-feature
```

### 커밋 및 푸시
```bash
# 변경사항 스테이징
git add .

# 커밋
git commit -m "feat: 기능 추가"

# 푸시
git push origin <branch-name>
```

## 유틸리티 명령어 (macOS)

### 파일 검색
```bash
# 파일 찾기
find . -name "*.py"

# 특정 내용 검색
grep -r "pattern" .

# 파일 목록
ls -la
```

### 프로세스 관리
```bash
# 포트 사용 확인
lsof -i :4449

# 프로세스 종료
kill -9 <PID>
```

### Python 관련
```bash
# Python 버전 확인
python --version

# 패키지 설치
pip install <package-name>

# 설치된 패키지 목록
pip list

# requirements.txt 생성
pip freeze > requirements.txt
```

## gRPC 관련

### Protobuf 컴파일
```bash
# proto 파일에서 Python 코드 생성
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/*.proto
```

## 데이터베이스

### MongoDB
- 연결은 앱 시작 시 자동으로 처리됨 (환경 변수 필요)
- Beanie를 통해 ODM 방식으로 접근

## 환경 변수
- `.env` 파일에 환경 변수 설정 필요
- 주요 환경 변수: MongoDB URI, Redis URI, OpenAI API Key, Pinecone API Key 등
