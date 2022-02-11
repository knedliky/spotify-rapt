import os

from flask import Flask, render_template, request

from client import spotify_client

app = Flask(__name__)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/callback", methods=["GET", "POST"])
def callback():
    args = request.args
    code = args.get("code")
    return f"The code payload is {code}!"


if __name__ == "__main__":
    app.run()
