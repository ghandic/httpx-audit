FROM python:3.10-alpine3.16

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

CMD ["opentelemetry-instrument", "gunicorn", "app:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80", "--threads", "1", "--worker-connections", "1000", "--timeout", "60", "--keep-alive", "60"]
