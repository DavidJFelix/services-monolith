#!/usr/bin/env python
from flask import abort, jsonify, Flask, request
from oauth2client import client, crypt
import platform
import socket

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify(status="UP", fullyQualifiedDomainName=socket.getfqdn(), node=platform.node())


@app.route("/auth/token-auth", methods=["POST"])
def token_auth():
    client_id = app.config['CLIENT_ID']
    android_client_id = app.config['ANDROID_CLIENT_ID']
    ios_client_id = app.config['IOS_CLIENT_ID']

    try:
        id_info = client.verifiy_id_token(request.data, app.config['CLIENT_ID'])
        if id_info['aud'] not in [android_client_id, ios_client_id]:
            raise crypt.AppIdentityError("Unrecognized client.")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise crypt.AppIdentityError("Wrong issuer.")
        if idinfo['hd'] != APPS_DOMAIN_NAME:
            raise crypt.AppIdentityError("Wrong hosted domain.")
    except crypt.AppIdentityError:
        abort(401)

    #TODO: Need to actually do something if the auth works
    pass


@app.errorhandler(401)
def not_authorized_error():
    return jsonify(error=401), 401


@app.errorhandler(404)
def not_found_error():
    return jsonify(error=404), 404


@app.errorhandler(500)
def internal_server_error():
    return jsonify(error=500), 500


if __name__ == "__main__":
    app.run()

