FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV NGROK_TOKEN=${NGROK_TOKEN}

WORKDIR /


RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz; \
    tar xvzf ./ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin;


COPY /domain /domain
COPY /repositories /repositories
COPY /services /services
COPY /scripts /scripts
COPY /util /util
COPY requirements.txt /
COPY main.py /
COPY celery_worker.py /
COPY gateway_bot.py /
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ngrok authtoken $NGROK_TOKEN && \
    python main.py && \
    nohup ngrok http --domain=loved-normally-hippo.ngrok-free.app 8000 > /dev/null &