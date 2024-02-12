FROM python:3.11-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.6.1

RUN apt-get update \
  && apt-get -y install gcc \
  && apt-get clean

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY . .

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
