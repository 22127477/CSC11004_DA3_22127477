# Sử dụng Python image nhẹ
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào
COPY . .

# Mở port 5000
EXPOSE 5000

# Lệnh chạy ứng dụng
CMD ["python", "app.py"]
