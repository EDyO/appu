FROM python:3.7-alpine

RUN apk --update add \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && rm /var/cache/apk/*

RUN addgroup -S appu -g 1000 \
    && adduser -S appu -G appu -u 1000

USER appu

COPY --chown=appu:appu . /home/appu

RUN mkdir -p /home/appu/files /home/appu/podcast

RUN cd /home/appu/ \
    && pip install -r requirements.txt

WORKDIR /home/appu

CMD ["/usr/local/bin/python", "/home/appu/appu.py"]