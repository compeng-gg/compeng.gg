FROM debian:trixie-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    clang \
    clangd \
    direnv \
    git \
    locales \
    man-db \
    manpages-dev \
    meson \
    nano \
    npm \
    python3-venv \
    vim \
    wget \
    zsh \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen

RUN sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)" "" --unattended \
    && sed -i 's/ZSH_THEME="robbyrussell"/ZSH_THEME="lukerandall"/g' /root/.zshrc \
    && echo '\nexport NEXT_PUBLIC_ORIGIN="https://${CODESPACE_NAME}-3000.app.github.dev"' \
            '\nexport NEXT_PUBLIC_API_URL="https://${CODESPACE_NAME}-8000.app.github.dev/api/v0"' \
            '\nexport CSRF_TRUSTED_ORIGINS='\''["https://'\''${CODESPACE_NAME}'\''-3000.app.github.dev"]'\' \
            '\nexport CORS_ALLOWED_ORIGINS='\''["https://'\''${CODESPACE_NAME}'\''-3000.app.github.dev"]'\' >> /root/.zshrc

CMD ["zsh"]
