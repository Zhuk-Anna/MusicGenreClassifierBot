FROM python:3.11-slim

WORKDIR /app

# Копируем requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем api код
COPY . /app/api

# Копируем папку models
COPY ../models /app/models

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]