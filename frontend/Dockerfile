FROM debian:trixie-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/compeng.gg

COPY . .
RUN npm ci && npm run build

EXPOSE 3000
ENV PORT 3000
CMD ["npm", "run", "start"]
