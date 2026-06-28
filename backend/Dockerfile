FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir tenacity neo4j 

# Copy backend code into a subfolder named 'backend'
COPY . ./backend

# Create non-root user and grant permissions
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
# Start FastAPI server, setting PYTHONPATH to /app so backend package is found
ENV PYTHONPATH=/app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
