# =========================
# BACKEND / WORKER
# =========================
FROM python:3.12-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY Backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =========================
# FRONTEND BUILD
# =========================
FROM node:22-alpine AS frontend-build

ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

WORKDIR /app

COPY banking-refund-frontend/banking-refund-frontend/package*.json ./
RUN npm install --no-audit --no-fund

COPY banking-refund-frontend/banking-refund-frontend/ .
RUN npm run build

# =========================
# FRONTEND PRODUCTION
# =========================
FROM node:22-alpine AS frontend

ENV NODE_ENV=production \
    PORT=3000

WORKDIR /app

COPY banking-refund-frontend/banking-refund-frontend/package*.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY --from=frontend-build /app/dist ./dist
COPY banking-refund-frontend/banking-refund-frontend/server.mjs ./server.mjs

EXPOSE 3000
CMD ["node", "server.mjs"]
