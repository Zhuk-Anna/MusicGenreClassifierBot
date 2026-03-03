FROM python:3.11-slim

WORKDIR /app

RUN mkdir tmp

COPY tg_bot/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY tg_bot /app/tg_bot

CMD ["python", "tg_bot/bot.py"]