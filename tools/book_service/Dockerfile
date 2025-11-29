
FROM python:3.9.15
RUN apt update && apt upgrade -y

ENV APP=/books
RUN mkdir $APP
WORKDIR $APP

RUN apt install make curl -y
RUN pip install --upgrade pip

# get and install poetry package manager
RUN curl -sSL https://install.python-poetry.org | python3 -
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH=/root/.local/bin:$PATH
# set poetry so it does not use a virtual environment in deployment container
RUN poetry config virtualenvs.create false

ENV PYTHONPATH=$APP
COPY ./pyproject.toml ./poetry.lock $APP/
RUN poetry install --no-root --without dev

COPY ./books $APP/
COPY ./config/* $APP/config/

EXPOSE 8083

ENTRYPOINT ["poetry","run","uwsgi","--ini","api.ini"]
