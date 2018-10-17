FROM python:3-slim

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=tempio.settings \
    DEBUG=false \
    DATA_DIR=/data

RUN cd /usr/share/man && mkdir -p man1 man2 man3 man4 man5 man6 man7 man8 man9 && \
    apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl ca-certificates postgresql-client nano && \
    rm -rf /usr/share/man/* && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -Ur /app/requirements.txt

COPY . /app

RUN set -x && \
    mkdir -p /data && \
    python /app/manage.py collectstatic --noinput && \
    python -m compileall -f -q /app && \
    find /app -type d -print0 | xargs -0 chmod 555 && \
    find /app -type f -print0 | xargs -0 chmod 444 && \
    chmod 555 /app/manage.py /app/docker-entrypoint.sh && \
    chown -R nobody:0 /app /data && \
    chmod g+s /app /data

WORKDIR /app
USER nobody

VOLUME ["/data"]

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["gunicorn", "-c", "gunicorn.conf", "--access-logfile", "-", "tempio.wsgi"]
