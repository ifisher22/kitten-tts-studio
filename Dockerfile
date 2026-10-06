# Multi-stage Dockerfile for Kitten TTS Application
# Stage 1: Backend (Python/FastAPI)
FROM python:3.11-slim as backend

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy model files (if they exist locally)
COPY config.json kitten_tts_mini_v0_8.onnx voices.npz* /app/

# Stage 2: Frontend (Node.js/Next.js)
FROM node:20-alpine as frontend

WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json .
RUN npm install

# Copy frontend code
COPY frontend/ .

# Build frontend
RUN npm run build

# Stage 3: Production
FROM python:3.11-slim as production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy model files
COPY config.json kitten_tts_mini_v0_8.onnx voices.npz* ./

# Copy built frontend
COPY --from=frontend /app/frontend/.next ./frontend/.next
COPY --from=frontend /app/frontend/package.json ./frontend/
COPY --from=frontend /app/frontend/public ./frontend/public

# Install Node.js for serving frontend (optional, can also use static export)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Expose ports
EXPOSE 8008 3000

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app/backend && uvicorn main:app --host 0.0.0.0 --port 8008 &\n\
cd /app/frontend && npm install next && npm start\n\
wait' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
