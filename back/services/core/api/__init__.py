import os

from flask import Flask, jsonify


app = Flask(__name__)


@app.route("/")
def hello_world():
    return jsonify(message="Hello world")

