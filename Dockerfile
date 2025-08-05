FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libxrender1 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копируем все файлы проекта
COPY . .

# Установка зависимостей Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["python", "main.py"]
