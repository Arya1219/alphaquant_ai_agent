FROM python:3.11-slim

WORKDIR /app

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies directly
RUN pip install --no-cache-dir \
    fastapi \
    "uvicorn[standard]" \
    openai \
    pandas \
    numpy \
    python-dotenv

# Copy source
COPY src/ ./src/
COPY AgentCard.json .

EXPOSE 10000

CMD ["python", "-m", "src"]
