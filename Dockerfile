FROM amd64/python:3.9.5-alpine3.13
LABEL maintainer "Lorenzo Prosseda <lerokamut@gmail.com>"

ADD ./app /app

RUN pip install -I -r /app/requirements.txt

WORKDIR /app
VOLUME ["/app"]

ENTRYPOINT ["python3", "main.py"]
