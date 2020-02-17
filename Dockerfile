FROM arm64v8/alpine:3.11

COPY qemu-aarch64-static /usr/bin/

ADD ./app /app

RUN apk add --no-cache py3-pip gcc python3-dev musl-dev libffi-dev openssl-dev libxml2-dev libxslt-dev && \
    pip3 install -U pip && pip3 install -U -r/app/requirements.txt

WORKDIR /app
VOLUME ["/app"]

RUN rm -rf /usr/bin/qemu-aarch64-static

ENTRYPOINT ["python3", "main.py"]
