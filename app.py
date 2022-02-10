import os

from flask import Flask, request

from client.oauth import *

app = Flask(__name__)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")


@app.route("/")
def home():
    return "Hello, Flask!"


@app.route("/callback", methods=["GET", "POST"])
def spotify_callback():
    args = request.args
    code = args.get("code")
    return f"The code payload is {code}!"


if __name__ == "__main__":
    app.run()
