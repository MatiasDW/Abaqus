FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# deps primero para cache
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# copia proyecto
COPY . /app

# espera simple a DB
COPY <<'BASH' /usr/local/bin/wait-for-db
#!/usr/bin/env bash
set -e
HOST=${POSTGRES_HOST:-db}
PORT=${POSTGRES_PORT:-5432}
until python - <<PY
import socket,sys
s=socket.socket()
try:
    s.connect(("${HOST}", int("${PORT}"))); sys.exit(0)
except Exception:
    sys.exit(1)
PY
do echo "DB not ready yet..."; sleep 2; done
BASH
RUN chmod +x /usr/local/bin/wait-for-db

EXPOSE 8000
CMD ["bash","-lc","wait-for-db && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
