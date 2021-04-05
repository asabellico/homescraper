FROM python:3.8

RUN mkdir /code /data
WORKDIR /code
COPY . /code/

RUN pip install .

CMD [ "homescraper", "/data/config.yml" ]
