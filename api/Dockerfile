FROM python:3.11-slim

WORKDIR /app

COPY api/requirements.txt .

RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY api /app/api

COPY models /app/models

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]