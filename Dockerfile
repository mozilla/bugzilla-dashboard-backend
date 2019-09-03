FROM python:slim

COPY . .

RUN python setup.py install

ENTRYPOINT ["./run.sh"]
