FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install fastapi uvicorn openai pandas numpy

EXPOSE 10000

CMD ["python", "-m", "src"]
