# =============================================================================
# Stage 1 — builder
# Install dependencies into a virtual environment
# =============================================================================
FROM public.ecr.aws/docker/library/python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip --quiet && \
    /venv/bin/pip install -r requirements.txt --quiet

# =============================================================================
# Stage 2 — runtime
# Copy only the venv and app source — no build tools
# =============================================================================
FROM public.ecr.aws/docker/library/python:3.12-slim AS runtime

# Non-root user for security
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /venv /venv

# Copy application source
COPY app.py .
COPY public/ ./public/

# Ensure non-root user owns the app directory
RUN chown -R appuser:appgroup /app

USER appuser

ENV PATH="/venv/bin:$PATH"
ENV APP_PORT=5000
ENV APP_HOST=0.0.0.0

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["python", "app.py"]