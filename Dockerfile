# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /obsidian-audio-capture
COPY . .

VOLUME /obsidian-audio-capture/var

RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "gunicorn", "-b", "0.0.0.0", "-t", "180", "app:create_app('config.json')"]