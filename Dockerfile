FROM ghcr.io/astral-sh/uv:alpine

COPY . .
RUN ["uv", "run", "."]
