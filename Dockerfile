FROM python:3

WORKDIR /usr/src/app

COPY . ./

RUN pip install -e . \
  pip install ghunt

COPY . .
CMD ["python", "./main.py"]
