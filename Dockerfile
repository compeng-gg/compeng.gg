FROM python:3.11.5-slim-bookworm

WORKDIR /opt/compeng.gg

COPY requirements.txt requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt
COPY . .
