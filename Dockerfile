# 베이스 이미지
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# Chromium 및 의존성 설치 (ARM64 및 AMD64 아키텍처 모두 지원)
RUN apt-get update && apt-get install -y \
    chromium \
    --no-install-recommends \
    # 설치 후 불필요한 apt 캐시를 정리하여 이미지 크기를 줄입니다.
    && rm -rf /var/lib/apt/lists/*

# 필요 파일 복사
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4449"]