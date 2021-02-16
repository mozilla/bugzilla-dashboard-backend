Bugzilla dashboard backend
===================
Backend to fetch details from bugzilla API for bugzilla dashboard

Setup
---------------
This is a Python 3 application, so it should be easy to bootstrap on your computer:
Create Virtual environment:
```
mkvirtualenv -p /usr/bin/python3 bugzilla-dashboard-backend
```
Install dependencies:
```
pip install -r requirements.txt -r requirements-dev.txt
```
To run the linting tests:
```
pre-commit run -a
```
To run tests:
```
pytest
```

Deployment
----------

For deployment, you will need to update the ci configuration with the git hash of this
project.
See https://bugzilla.mozilla.org/show_bug.cgi?id=1691378 as example.
