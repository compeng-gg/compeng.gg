FROM debian:trixie-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    podman \
    python3 \
    python3-venv \
    ssh \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"  -o /usr/local/bin/kubectl \
  && chmod +x /usr/local/bin/kubectl

RUN groupadd -g 1000 compeng \
  && useradd -u 1000 -g 1000 -m -s /bin/bash compeng

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
RUN chown -R 1000:1000 /opt/compeng.gg/

EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "compeng_gg.asgi:application"]
