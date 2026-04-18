FROM python:3.12-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv and create non-root user
RUN pip install --no-cache-dir uv && \
    useradd -m -u 1000 -s /bin/bash appuser

WORKDIR /app

# Copy dependency files first for better layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev && chown -R appuser:appuser /app/.venv

# Copy bot code
COPY --chown=appuser:appuser bot/ ./bot/

# Switch to non-root user
USER appuser

EXPOSE 8080

# Health check - verify bot module can be imported
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import bot.main; import sys; sys.exit(0)" || exit 1

# Graceful shutdown
STOPSIGNAL SIGTERM

CMD ["uv", "run", "python", "-m", "bot.main"]
