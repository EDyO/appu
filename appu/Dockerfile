FROM python:3.7-alpine

VOLUME /home/appu/.aws
VOLUME /home/appu/cfg
VOLUME /home/appu/files
VOLUME /home/appu/podcast

RUN apk --update add \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && rm /var/cache/apk/*

RUN addgroup -S appu -g 1000 \
    && adduser -S appu -G appu -u 1000

USER appu

COPY --chown=appu:appu . /home/appu

RUN cd /home/appu/ \
    && pip install --user -r requirements.txt

WORKDIR /home/appu

CMD ["/usr/local/bin/python", "/home/appu/appu.py"]