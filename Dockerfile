# syntax=docker/dockerfile:1.6

# ----- Builder stage -----
FROM python:3.12-slim AS builder
WORKDIR /build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# ----- Runtime stage -----
FROM python:3.12-slim AS runtime
LABEL org.opencontainers.image.title="ACEest Fitness"
LABEL org.opencontainers.image.source="https://github.com/atul411/devops-assignment-2"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/app/.local/bin:${PATH}" \
    DATABASE=/data/aceest_fitness.db \
    FEATURE_LEVEL=3 \
    APP_VERSION=3.0.0

RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /data \
    && chown -R app:app /data
USER app
WORKDIR /home/app

COPY --from=builder --chown=app:app /root/.local /home/app/.local
COPY --chown=app:app app ./app
COPY --chown=app:app gunicorn.conf.py ./

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://localhost:5000/health',timeout=2).status==200 else 1)"

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
