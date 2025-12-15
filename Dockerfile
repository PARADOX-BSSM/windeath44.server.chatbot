# ✅ ARM64용 Python slim 이미지 사용
FROM --platform=linux/arm64 python:3.11-slim

# ✅ 작업 디렉토리 설정
WORKDIR /app

# ✅ chromium, chromedriver 및 의존성 설치
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libgbm1 \
    xdg-utils \
    wget \
    unzip \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# ✅ 환경 변수 설정 (undetected_chromedriver에서 자동 감지 가능하지만 명시적으로 지정)
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --headless=new"

# ✅ Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ 앱 복사
COPY . .

# ✅ FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4449"]
