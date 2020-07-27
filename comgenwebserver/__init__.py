import secrets
from flask import Flask
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)	
import comgenwebserver.github
# https://flask.palletsprojects.com/en/1.1.x/patterns/packages/

if __name__ == "__main__":
    app.run()
