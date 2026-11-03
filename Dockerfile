FROM python:3.10-slim

WORKDIR /app/backend

COPY requirements.docker.txt /app/
COPY requirements.ai.txt /app/

RUN pip install --no-cache-dir -r /app/requirements.docker.txt

COPY backend/ /app/backend/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]