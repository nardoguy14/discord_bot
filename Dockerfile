FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV NGROK_TOKEN=${NGROK_TOKEN}

WORKDIR /

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

CMD python main.py