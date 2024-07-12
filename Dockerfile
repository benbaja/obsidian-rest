# syntax=docker/dockerfile:1
FROM python:3.11-slim-buster

WORKDIR /obsidian-audio-capture
COPY . .

VOLUME /obsidian-audio-capture/var
EXPOSE 8000
ARG nginx=false

#RUN if [ "$nginx" = "false" ]; then mkdir -p /obsidian-audio-capture/var/socket; fi
RUN echo "python3 -m gunicorn -b $([ "$nginx" = "false" ] && echo 0.0.0.0 || echo unix:/obsidian-audio-capture/var/oac.sock) -t 180 \"app:create_app('config.json')\"" > start.sh
RUN chmod +x start.sh

RUN pip3 install -r requirements.txt

CMD ./start.sh
#CMD ["python3", "-m", "gunicorn", "-b", "0.0.0.0", "-t", "180", "app:create_app('config.json')"]