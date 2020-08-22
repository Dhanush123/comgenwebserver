import secrets
from flask import Flask
app = Flask(__name__)
# https://flask.palletsprojects.com/en/1.1.x/patterns/packages/
app.secret_key = secrets.token_urlsafe(32)	
import comgenwebserver.endpoints.auth
import comgenwebserver.endpoints.github
from comgenwebserver.helpers.scheduler import comment_commit_files

import atexit
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(func=comment_commit_files, trigger="interval", seconds=15)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run()