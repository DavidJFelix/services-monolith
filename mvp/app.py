#!/usr/bin/env python
from flask import abort, jsonify, Flask, request
from oauth2client import client, crypt
from sqlalchemy import create_engine, MetaData, Table
import platform
import socket


app = Flask(__name__)
engine = create_engine('postgresql://dev:password@ds-dev.clqblfd0mdpm.us-east-1.rds.amazonaws.com:5432/dev')
metadata = MetaData(bind=engine)
users = Table('users', metadata, autoload=True)
oauth_providers = Table('oauth_providers', metadata, autoload=True)
oauth_claims = Table('oauth_claims', metadata, autoload=True)


@app.route("/", methods=["GET"])
def handle_hateos_index():
    resp = {
        'healthcheck_url': request.base_url + 'health',
    }
    return jsonify(**resp)
        

@app.route("/health", methods=["GET"])
def handle_health():
    resp = {
        'status': 'UP',
        'fullyQualifiedDomainName': socket.getfqdn(),
        'node': platform.node(),
    }
    return jsonify(**resp)


@app.route("/user", methods=["GET", "POST"])
def handle_user():
    resp = {
        'id': '8ad0e654-f569-43f5-83d0-97d040016943',
    }
    # Return NOT IMPLEMENTED
    return jsonify(**resp), 501


@app.route("/address" methods=["GET", "POST"])
def handle_address():
    resp = {
        'id': '8ad0e654-f569-43f5-83d0-97d040016943',
    }
    # Return NOT IMPLEMENTED
    return jsonify(**resp), 501


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
    resp = {
        "token": {
            "type" "bearer"
        }
    }
    return jsonify(**resp), 501


@app.errorhandler(401)
def handle_not_authorized_error(*_):
    return jsonify(error=401), 401


@app.errorhandler(404)
def handle_not_found_error(*_):
    return jsonify(error=404), 404


@app.errorhandler(500)
def handle_internal_server_error(*_):
    return jsonify(error=500), 500


if __name__ == "__main__":
    app.run()

