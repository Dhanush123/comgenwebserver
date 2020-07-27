import os

import requests
from flask import session, request, jsonify
from flask_cors import cross_origin

from comgenwebserver import app

token_url = 'https://github.com/login/oauth/access_token'


@app.route('/githubcodetotoken', methods=['GET', 'POST'])
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def handle_callback():
    '''
        temp code -> perm access token
    '''
    if 'code' in request.args:
        payload = {
            'client_id': os.environ['GITHUB_CLIENT_ID'],
            'client_secret': os.environ['GITHUB_CLIENT_SECRET'],
            'code': request.args['code']
        }
        headers = {'Accept': 'application/json'}
        req = requests.post(token_url, params=payload, headers=headers)
        resp = req.json()

        if 'access_token' in resp:
            session['access_token'] = resp['access_token']
            return jsonify(access_token=resp['access_token'])
        else:
            return jsonify(error='Error retrieving access_token'), 404
    else:
        return jsonify(error="Didn't receive code"), 404
