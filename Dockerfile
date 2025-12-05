FROM ghcr.io/astral-sh/uv:alpine

RUN apk add --no-cache --update musl musl-utils musl-locales tzdata
ENV TZ="Europe/Berlin"

ADD . /app
WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "."]
