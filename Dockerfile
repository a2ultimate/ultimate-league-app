FROM python:3.9-slim-trixie AS python-base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
    default-mysql-client \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/src

COPY src/requirements/ /app/src/requirements/


FROM python-base AS development

RUN pip install --no-cache-dir -r requirements/dev.txt

CMD ["python", "manage.py", "runserver_plus", "0.0.0.0:8000"]


FROM node:20.19.5-trixie-slim AS frontend-base

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
    g++ \
    make \
    python3 \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/src/static


FROM frontend-base AS frontend-build

COPY src/static/package.json src/static/package-lock.json ./
RUN npm install --global npm@8.19.2 && npm ci

COPY src/static/ ./
RUN npm run build


FROM python-base AS production

RUN pip install --no-cache-dir -r requirements/prod.txt

COPY src/ /app/src/
COPY --from=frontend-build /app/src/static/build/ /app/src/static/build/

CMD ["gunicorn", "--bind=0.0.0.0:8001", "--worker-class=gevent", "ultimate.wsgi:application"]
