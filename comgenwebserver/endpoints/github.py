import os

import requests
from flask import session, request, jsonify
from flask_cors import cross_origin

from comgenwebserver import app
from comgenwebserver.constants import GITHUB_ACCESS_TOKEN_URL
from comgenwebserver.db.service import DBClient


@app.route('/getusergithubrepos', methods=['GET'])
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def get_user_github_repos():
    try:
        access_token = request.args['access_token']
        db = DBClient(access_token)
        user_repos_info = db.get_relevant_repos_info()
        return jsonify(user_repos_info=user_repos_info), 200
    except Exception as e:
        return jsonify(error="error in get_user_repos"), 404


@app.route('/toggletrackgithubrepo', methods=['POST'])
@cross_origin(origin='localhost', headers=['Content-Type', 'Authorization'])
def track_github_repo():
    try:
        access_token = request.args['access_token']
        repo_id = request.args['repo_id']
        toggle_status = request.args['toggle_status'] == 'true'
        db = DBClient(access_token)
        success_status = db.toggle_repo_tracking_status(repo_id, toggle_status)
        return jsonify(success=success_status)
    except Exception as e:
        return jsonify(error="error in get_user_repos"), 404
