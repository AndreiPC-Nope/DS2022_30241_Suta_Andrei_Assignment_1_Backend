FROM python:3.8-slim-buster

WORKDIR /app

RUN apt update
RUN apt install gcc -y
RUN apt install libpq-dev -y

RUN pip install gunicorn

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


COPY . .

CMD [ "gunicorn", "-b", "0.0.0.0:5000", "app:app"]
