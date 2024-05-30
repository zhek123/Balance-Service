
FROM python:3.10-slim-buster

WORKDIR /src

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements /src/requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/base.txt


COPY app /src/app

EXPOSE 8000

ENTRYPOINT ["python", "-m", "app"]
