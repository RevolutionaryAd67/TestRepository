FROM python:3.11-slim

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

COPY pyproject.toml README.md ./
COPY app ./app
COPY tests ./tests

RUN pip install --upgrade pip \
    && pip install -e .

EXPOSE 8080 2404

CMD ["python", "-m", "hypercorn", "app.main:app", "--bind", "0.0.0.0:8080", "--workers", "1", "--access-log", "-"]
