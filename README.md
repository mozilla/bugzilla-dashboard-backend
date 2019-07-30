Bugzilla dashboard backend
===================
Backend to fetch details from bugzilla API for bugzilla dashboard

Setup
---------------
This is a Python 3 application, so it should be easy to bootstrap on your computer:
Create Virtal environment:
```
mkvirtualenv -p /usr/bin/python3 bugzilla-dashboard-flask
```
Install dependencies:
```
pip install -r requirements.txt -r requirements-dev.txt
```
To run the linting tests:
```
flake8
```
To run tests:
```
pytest
```