FROM python:3.11-slim

WORKDIR /app

# Install system packages required for building psycopg2 and running health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend codebase
COPY . .

# Ensure storage directories exist
RUN mkdir -p uploads/institution_logos uploads/student_photos backups

EXPOSE 8000

# Run database migrations with alembic, then start uvicorn
CMD ["sh", "-c", "alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
