FROM python:slim

COPY . .

RUN python setup.py install

ENTRYPOINT ["python", "-m", "bugzilla_dashboard.component_queries"]
