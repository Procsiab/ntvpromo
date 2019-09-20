FROM alpine:latest

ADD ./app /app

RUN apk add --no-cache py3-pip gcc python3-dev musl-dev libffi-dev openssl-dev libxml2-dev libxslt-dev && \
    pip3 install -U pip && pip3 install -U -r/app/requirements.txt

WORKDIR /app
VOLUME ["/app"]

ENTRYPOINT ["python3", "main.py"]