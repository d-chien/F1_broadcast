FROM python:3.10-slim-buster

WORKDIR /app

# 將 pyproject.toml 和 poetry.lock 複製到工作目錄
COPY requirements.txt ./

# 安裝 Poetry
RUN pip install --no-cache-dir -r requirements.txt

# 將應用程式程式碼複製到工作目錄
COPY . .

EXPOSE 8080

# 設定啟動命令
CMD ["python","app.py"]
