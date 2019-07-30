from flask import Flask

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return {
        "status": 404,
        "message": "Not found"
    }
