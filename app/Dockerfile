# Stage 1: builder, installs dependencies
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: final, small runtime image
FROM python:3.12-slim
WORKDIR /app
RUN useradd -r -u 1001 appuser
COPY --from=builder /install /usr/local
COPY app.py .
USER appuser
ENV APP_NAME=myapp REDIS_HOST=redis
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
