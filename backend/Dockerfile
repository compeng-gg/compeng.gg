FROM debian:trixie-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-venv \
    ssh \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/compeng.gg

ENV VIRTUAL_ENV=/opt/compeng.gg/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH="/opt/compeng.gg"

COPY requirements.txt requirements.txt
RUN pip install daphne "psycopg[binary]"
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic

EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "compeng_gg.asgi:application"]
