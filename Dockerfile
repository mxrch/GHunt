FROM python:3.8.6-slim-buster

ENV CHROMEDRIVER_VERSION 85.0.4183.87
ENV CHROME_VERSION 85.0.4183.121-1

WORKDIR /usr/src/app

RUN groupadd -r app && adduser --system --home /home/app --ingroup app app && \
    chown -R app:app /usr/src/app && \
    apt-get update && \
    apt-get install -y curl unzip gnupg && \
    curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable=${CHROME_VERSION} && \
    rm -rf /var/lib/apt/lists/*

RUN curl -O https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm -f chromedriver_linux64.zip

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER app

ENTRYPOINT [ "python3" ]
