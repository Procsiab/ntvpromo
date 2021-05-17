ARG PYTHON_VERSION=3.9.5-alpine3.13

# Builder image for generating Python wheels
FROM amd64/python:${PYTHON_VERSION} AS builder

ENV PYTHONUNBUFFERED 1
RUN apk add --no-cache \
    git \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    openssl-dev \
    libxml2-dev \
    libxslt-dev

WORKDIR /wheels
COPY ./app/requirements.txt /wheels/requirements.txt

RUN pip wheel -r ./requirements.txt


# Final container image for the application
FROM amd64/python:${PYTHON_VERSION}
LABEL maintainer "Lorenzo Prosseda <lerokamut@gmail.com>"

ENV PYTHONUNBUFFERED 1
ENV TZ Europe/Rome
ADD ./app /app
COPY --from=builder /wheels /wheels

RUN apk add --no-cache \
    libxml2 \
    libxslt \
    libstdc++ \
    && rm -rf /var/cache/apk/*

RUN pip install --no-cache-dir \
    -r /app/requirements-deploy.txt \
    -f /wheels \
    && rm -rf /wheels

WORKDIR /app
VOLUME ["/secrets"]

ENTRYPOINT ["python3", "main.py"]
