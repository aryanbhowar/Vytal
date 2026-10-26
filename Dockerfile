# Vytal container image: builds the frontend, then runs one Python process that
# serves both the website and the API.
#
# STATUS: NOT VERIFIED. Docker was not installed on the development machine, so
# this image has never been built or run. Verify with:
#   docker build -t vytal:0.2.0 .
#   docker run --rm -p 8000:8000 vytal:0.2.0
# and check http://localhost:8000/api/health/ready before relying on it.

# ---- Stage 1: build the frontend ----
FROM node:24-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: runtime ----
FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VYTAL_SERVE_FRONTEND=true \
    VYTAL_ENABLE_API_DOCS=false \
    VYTAL_FRONTEND_DIST=/app/frontend/dist \
    VYTAL_MODELS_DIR=/app/models

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Only what the server needs: no datasets, no training code, no tests.
COPY backend/app backend/app
COPY ml/__init__.py ml/__init__.py
COPY ml/feature_definitions ml/feature_definitions
COPY ml/inference ml/inference
COPY models models
COPY --from=frontend /build/frontend/dist frontend/dist

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 vytal && chown -R vytal /app
USER vytal

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health/ready', timeout=4).status == 200 else 1)"

# --proxy-headers lets the rate limiter see real client IPs when a trusted reverse
# proxy sets X-Forwarded-For. Restrict --forwarded-allow-ips to your proxy's address.
CMD ["python", "-m", "uvicorn", "app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--no-server-header", "--proxy-headers", "--forwarded-allow-ips", "127.0.0.1"]
