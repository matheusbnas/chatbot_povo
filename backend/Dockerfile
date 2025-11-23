# ============================================
# STAGE 1: Builder (para produção)
# ============================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies to a temporary location
RUN pip install --no-cache-dir --target /app/deps -r requirements.txt

# ============================================
# STAGE 2: Production
# ============================================
FROM python:3.11-slim AS production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user first
RUN useradd -m -u 1000 appuser

# Copy Python dependencies from builder
COPY --from=builder /app/deps /app/deps

# Copy application
COPY . .

# Make sure scripts are executable
RUN chmod +x /app/scripts/*.py 2>/dev/null || true

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add deps to Python path
# Quando pip install --target é usado, os módulos ficam em lib/python3.11/site-packages
# Mas podemos adicionar /app/deps diretamente e Python encontrará automaticamente
ENV PYTHONPATH=/app/deps/lib/python3.11/site-packages:/app:$PYTHONPATH
ENV PATH=/app/deps/bin:$PATH

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Run application (sem reload em produção, com workers)
# Usar python -m para garantir que encontre os módulos
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]

# ============================================
# STAGE 3: Development
# ============================================
FROM python:3.11-slim AS development

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Run application (com reload para desenvolvimento)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
