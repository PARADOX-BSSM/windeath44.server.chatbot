# Task Completion Checklist

작업 완료 시 확인해야 할 사항들입니다.

## 코드 작성 후

### 1. 코드 품질 확인
- [ ] 타입 힌트가 모든 함수 파라미터와 반환값에 추가되었는가?
- [ ] 비동기 함수에서 `await` 키워드를 올바르게 사용했는가?
- [ ] 예외 처리가 적절히 구현되었는가? (BusinessException 활용)
- [ ] 코드에 한글 주석이 적절히 추가되었는가?

### 2. FastAPI 패턴 준수
- [ ] 라우터가 적절한 prefix와 tags로 구성되었는가?
- [ ] 의존성 주입이 Depends를 통해 올바르게 구현되었는가?
- [ ] 응답이 BaseResponse 형식을 따르는가?

### 3. Import 정리
- [ ] Import가 표준 라이브러리 → 서드파티 → 로컬 순서로 정렬되었는가?
- [ ] 사용하지 않는 import가 제거되었는가?

## 테스트

### 4. 기능 테스트
- [ ] pytest로 테스트 코드를 작성했는가? (필요 시)
- [ ] 비동기 함수 테스트에 `pytest-asyncio` 사용했는가?
- [ ] 모든 테스트가 통과하는가?
```bash
pytest
```

### 5. 로컬 실행 테스트
- [ ] 로컬에서 서버가 정상적으로 실행되는가?
```bash
uvicorn main:app --host 0.0.0.0 --port 4449 --reload
```
- [ ] Swagger UI (http://localhost:4449/docs)에서 API가 정상 작동하는가?
- [ ] 변경된 엔드포인트를 직접 테스트했는가?

## Docker 및 배포

### 6. Docker 빌드 확인 (필요 시)
- [ ] Dockerfile이 변경되었다면, 빌드가 성공하는가?
```bash
docker build -t fastapi-project .
```
- [ ] 컨테이너가 정상적으로 실행되는가?
```bash
docker run -p 4449:4449 fastapi-project
```

## Git 및 버전 관리

### 7. Git 커밋 전
- [ ] `.env` 파일이나 민감한 정보가 커밋에 포함되지 않았는가?
- [ ] 디버깅용 print 문이나 임시 코드가 제거되었는가?
- [ ] Git status를 확인하고 의도한 파일만 스테이징했는가?
```bash
git status
git diff
```

### 8. 커밋 메시지
- [ ] 커밋 메시지가 명확하고 의미있는가?
- [ ] 커밋 메시지 형식: `feat:`, `fix:`, `refactor:`, `docs:` 등 prefix 사용

## 코드 리뷰 준비

### 9. 문서화
- [ ] 중요한 비즈니스 로직에 주석이나 docstring이 추가되었는가?
- [ ] API 변경사항이 있다면 문서를 업데이트했는가?

### 10. 성능 및 보안
- [ ] N+1 쿼리 문제가 없는가?
- [ ] 민감한 정보가 로그에 출력되지 않는가?
- [ ] 인증/권한 체크가 필요한 엔드포인트에 적용되었는가? (get_user_id 의존성 등)

## 배포 전 최종 확인

### 11. 의존성 관리
- [ ] 새로운 패키지를 설치했다면 requirements.txt에 추가되었는가?
```bash
pip freeze > requirements.txt
```

### 12. 환경 변수
- [ ] 새로운 환경 변수가 추가되었다면 문서화되었는가?
- [ ] 프로덕션 환경에 필요한 환경 변수가 설정되었는가?

## gRPC 관련 (해당 시)

### 13. Protobuf 변경
- [ ] .proto 파일이 변경되었다면 Python 코드를 재생성했는가?
```bash
python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. ./protos/*.proto
```

## 참고사항
- 모든 체크리스트가 필수는 아니며, 작업의 성격에 따라 선택적으로 확인
- 중요한 변경사항이나 새로운 기능 추가 시에는 더 철저히 검토
