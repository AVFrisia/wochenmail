FROM python:latest

RUN pip install poetry
COPY . .
RUN poetry install
ENTRYPOINT ["poetry", "run", "python", "-m", "wochenmail.main"]
