FROM debian:trixie-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/compeng.gg

COPY package-lock.json package.json .
RUN npm ci
COPY . .
RUN npm run build

EXPOSE 3000
ENV PORT=3000
CMD ["sh", "-c", "npm run build && npm run start"]