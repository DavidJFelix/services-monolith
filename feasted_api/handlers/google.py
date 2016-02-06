from tornado import gen
from tornado.escape import utf8
from tornado.httpclient import HTTPError
from tornado.web import Finish

from .base import DefaultHandler
from ..lib.token import (
    decode_jwt,
    is_audience_in,
    is_google_jwt_valid,
)
from ..models.bearer_token import (
    create_bearer_token,
    generate_bearer_token,
)
from ..models.google_oauth_claim import get_google_oauth_claim


class GoogleAuthTokenHandler(DefaultHandler):
    @gen.coroutine
    def post(self):
        # Get JWT from body and convert it to dictionary
        token = utf8(self.request.body)
        decoded_token = decode_jwt(token)
        google_certs = yield self.application.get_google_certs()
        if decoded_token is None:
            raise HTTPError(400, "Could not parse JWT")

        # Validate JWT is signed by google, issuer is correct and it's within exp
        is_iss = yield is_google_jwt_valid(token, decoded_token, google_certs)
        if not is_iss:
            raise HTTPError(401, "JWT signature invalid")

        # Check that the JWT is signed with our app as the aud
        is_aud = is_audience_in(decoded_token, self.application.client_ids)
        if not is_aud:
            raise HTTPError(401, "JWT aud is not valid")

        # Get the google user id from the sub field
        provider_uid = decoded_token.get('sub', None)
        if provider_uid is None:
            raise HTTPError(400, "JWT contained no sub field")

        # Map the provider_uid to the user_id
        conn = yield self.db_conn()
        claim = yield get_google_oauth_claim(provider_uid, conn)
        if claim is None:
            # Create new user from JWT info
            pass

        bearer_token = generate_bearer_token()
        new_bearer_token = yield create_bearer_token(bearer_token, claim.user_id, conn)

        if new_bearer_token is None:
            raise HTTPError(500, "Could not create bearer token")

        token_container = {
            "type": "Bearer",
            "data": new_bearer_token.token,
        }
        self.set_status(200)
        self.write(token_container)
        raise Finish()
