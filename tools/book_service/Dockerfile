
FROM python:3.8.13
RUN apt update && apt upgrade -y

ENV APP /books
RUN mkdir $APP
WORKDIR $APP

RUN apt install make curl -y
RUN pip install --upgrade pip

# get and install poetry package manager
RUN curl -sSL https://install.python-poetry.org | python3 -
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH /root/.local/bin:$PATH
# set poetry so it does not use a virtual environment in deployment container
RUN poetry config virtualenvs.create false

ENV PYTHONPATH $APP
COPY ./pyproject.toml ./poetry.lock $APP/
RUN poetry install --no-dev

COPY ./books $APP/
COPY ./config/* $APP/config/

# Set an env variable from the build arg that is substituted at runtime
#ARG MY_SERVICE_NAME
#ENV ENV_MY_SERVICE_NAME=$MY_SERVICE_NAME

#ENTRYPOINT poetry run python api.py
#ENTRYPOINT uwsgi -s /tmp/yourapplication.sock --manage-script-name --mount /books=api
ENTRYPOINT poetry run uwsgi --ini api.ini
