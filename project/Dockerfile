FROM python:2.7

EXPOSE 3111

COPY ./techtrends .

RUN pip install -r requirements.txt

RUN python init_db.py

CMD [ "python", "app.py"]
