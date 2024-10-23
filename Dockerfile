# Используем базовый образ Python
FROM python:3.9-slim

# Установим рабочую директорию в контейнере
WORKDIR /app

# Скопируем все файлы в контейнер
COPY . /app

# Установим системные зависимости (включая pyodbc для SQL Server)
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get install -y unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Установим Python-зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Установим драйверы для MS SQL Server
RUN pip install pyodbc

# Откроем порт для приложения
EXPOSE 8000

# Запустим приложение через Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]