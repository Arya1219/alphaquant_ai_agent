FROM python:3.11-slim

WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn openai pandas numpy

# Expose port
EXPOSE 10000

# Run app
CMD ["uvicorn", "src.__main__:app", "--host", "0.0.0.0", "--port", "10000"]
