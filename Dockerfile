FROM python:3.13-slim-bookworm

ENV PYTHONWARNINGS=ignore::SyntaxWarning

VOLUME /home/appu/.aws

RUN apt update \
    && apt upgrade -y \
    && apt install -y \
        ffmpeg

COPY --from=ghcr.io/astral-sh/uv:0.5.26 /uv /uvx /bin

RUN addgroup --gid 1000 appu \
    && adduser --uid 1000 --ingroup appu appu

USER appu

COPY --chown=appu:appu \
    pyproject.toml \
    src/ \
    uv.lock \
    /home/appu

RUN cd /home/appu/ \
    && /bin/uv sync

WORKDIR /home/appu

CMD ["/bin/uv", "run", "appu"]
