FROM python:3.12.3-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./backend/

# Set Python Path
ENV PYTHONPATH=/app

# Command to run the application using Railway's dynamic PORT variable
CMD sh -c "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"
