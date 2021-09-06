ARG python_version=3.9.7

FROM python:$python_version
ENV TELEGRAM_UPLOAD_CONFIG_DIRECTORY=/config
ENV PYTHONPATH=/app/
VOLUME /config
VOLUME /files

RUN mkdir /app
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY telegram_upload/ /app/telegram_upload/
WORKDIR /files

ENTRYPOINT ["/usr/local/bin/python", "/app/telegram_upload/management.py"]
