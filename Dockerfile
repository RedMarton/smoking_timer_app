FROM python:3.12-slim-bookworm

WORKDIR /app

RUN pip install Flask psycopg2-binary

COPY ./src /app

CMD ["flask", "run", "--host=0.0.0.0"]