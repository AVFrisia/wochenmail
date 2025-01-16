FROM python

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

RUN pip install poetry
COPY . .
RUN poetry install
ENTRYPOINT ["poetry", "run", "python", "-m", "wochenmail"]
