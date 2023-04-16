FROM python:3.10-slim-bullseye

WORKDIR /home

# Set up libraries
RUN python3 -m venv .venv
RUN .venv/bin/pip install poetry

COPY ./poetry.lock .
COPY ./pyproject.toml .
COPY ./requirements.txt .
COPY ./README.md .

COPY ./st_app ./st_app
COPY ./the_project_tracker ./the_project_tracker

# This line needs ./the_project_tracker for some reason. However this order
# will make that changes in ./st_app invalidate the docker cache for the
# installed packages
RUN .venv/bin/python3 -m poetry install #-E st_app

# TODO: script to check if db is populated else populate it?

# TODO: make docker run app as non sudo?

COPY ./src ./src
RUN chmod +x ./src/run_app.sh

CMD ["./src/run_app.sh"]