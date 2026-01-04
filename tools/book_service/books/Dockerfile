FROM python:3.11-slim

LABEL maintainer="Books Server"
LABEL description="Server for Books Database"

# Set working directory
ENV APP=/books
RUN mkdir $APP
WORKDIR $APP

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

#RUN apt-get -y install curl
RUN pip install --no-cache-dir --upgrade pip
RUN pip install pipx
RUN pipx install poetry

# get and install poetry package manager
#RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=/root/.local/bin:$PATH
# set poetry so it does not use a virtual environment in deployment container
RUN poetry config virtualenvs.create false

ENV PYTHONPATH=$APP
COPY ./pyproject.toml ./poetry.lock $APP/
RUN poetry install --no-root --without dev

COPY ./book_service/books $APP/
COPY ./book_service/booksdb/* $APP/booksdb/
COPY ./book_service/config/* $APP/config/

RUN mkdir $APP/uploads

ENV BOOKSDB_CONFIG="./$APP/config/configuration.json"

EXPOSE 8083

ENTRYPOINT ["poetry","run","uwsgi","--ini","api.ini"]
