FROM python:slim

COPY . .

RUN pip install --no-cache-dir -r /requirements.txt && \
    python setup.py install

ENTRYPOINT ["python", "-m", "bugzilla_dashboard.component_queries"]
