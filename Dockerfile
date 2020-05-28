FROM amd64/alpine:3.11.6
LABEL maintainer "Lorenzo Prosseda <lerokamut@gmail.com>"

ADD ./app /app

RUN apk add --no-cache \
    python3=~3.8 \
    gcc=~9 \
    python3-dev=~3.8 \
    musl-dev=~1.1 \
    libffi-dev=~3.2 \
    openssl-dev=~1.1 \
    libxml2-dev=~2.9 \
    libxslt-dev=~1.1 && \
    pip3 install -I pip==20.1.1 && pip3 install -I -r /app/requirements.txt

WORKDIR /app
VOLUME ["/app"]

ENTRYPOINT ["python3", "main.py"]
