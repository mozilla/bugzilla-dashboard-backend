FROM python:slim

COPY requirements.txt /requirements.txt

RUN pip install --disable-pip-version-check --no-cache-dir -r /requirements.txt

COPY . /tmp/bzdata

WORKDIR /tmp/bzdata

ENTRYPOINT ["python", "-m", "bugzilla_dashboard.component_queries"]
