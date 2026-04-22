FROM python:3.11-slim

WORKDIR /app

# Copy dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Expose port
EXPOSE 8080

# Run the FastAPI app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
