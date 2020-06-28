FROM python:3.7-slim

WORKDIR /home/ezino/ew-bot

RUN pip3 install python-telegram-bot==12.7

COPY app.py data.py reply.py values.py ./

ENTRYPOINT python3 app.py