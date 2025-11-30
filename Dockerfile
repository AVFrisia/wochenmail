FROM ghcr.io/astral-sh/uv:alpine

COPY . .
ENTRYPOINT ["uv", "run", "."]
