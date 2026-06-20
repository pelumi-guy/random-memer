# ==========================================
# Stage 1: Build dependencies
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Install build dependencies for compilation (specifically for lxml and Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Production runtime env
# ==========================================
FROM python:3.10-slim AS runner

WORKDIR /app

# Install runtime dependencies for lxml
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application files
COPY . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

# Create a non-privileged user and configure permissions
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Health check using python urllib to query the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Start the application
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} app:app"]
