# Flask Skeleton App

## Installation
Create a [virtualenvironment](https://virtualenv.pypa.io/en/latest/) using Python 3 for the app. We recommend using 
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):
```bash
mkvirtualenv flask-skeleton
```
Then install the dependencies:
```bash
pip install -r requirements.txt
```
## Running
The Flask app can be run by doing:
```bash
FLASK_APP=app.py  FLASK_ENV=development flask run
```

