FROM ghcr.io/astral-sh/uv:debian

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install \
        locales && \
    rm -r /var/lib/apt/lists/*

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure locales

ENV TZ="Europe/Berlin"

ADD . /app
WORKDIR /app
RUN uv sync --locked

CMD ["uv", "run", "."]
