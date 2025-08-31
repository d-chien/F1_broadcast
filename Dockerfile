# 使用官方的 Python 3.10 映像檔
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 將 requirements.txt 複製到容器內
COPY requirements.txt .

# 使用 pip 安裝所有依賴套件
RUN pip install --no-cache-dir -r requirements.txt

# 將應用程式程式碼複製到工作目錄
COPY . .

# Cloud Run 會將 PORT 環境變數注入到容器中
# CMD 指令將使用這個變數來啟動 Uvicorn 伺服器
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]