FROM python:3.10 as base

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY localization/ /whiterabbit/localization
COPY resources/ /whiterabbit/resources
COPY src/ /whiterabbit/src
COPY example.env /whiterabbit/.env
COPY card_lists /whiterabbit/card_lists

workdir /whiterabbit

CMD [ "python", "./src"]
