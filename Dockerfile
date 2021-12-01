FROM python:3.8.6-slim-buster

ARG UID=1000
ARG GID=1000

WORKDIR /usr/src/app

RUN groupadd -o -g ${GID} -r app && adduser --system --home /home/app --ingroup app --uid ${UID} app && \
    chown -R app:app /usr/src/app && \
    apt-get update && \
    apt-get install -y curl unzip gnupg && \
    curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

COPY --chown=app:app requirements.txt docker/download_chromedriver.py ./

RUN python3 -m pip install --no-cache-dir -r requirements.txt && \
    python3 download_chromedriver.py && chown -R app:app /usr/src/app

COPY --chown=app:app . .

USER app

ENTRYPOINT [ "python3" ]
