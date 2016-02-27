import uuid

from tornado import gen
from tornado.escape import to_unicode, utf8
from tornado.web import Finish, HTTPError

from .base import BaseBearerAuthHandler
from ..lib.token import is_audience_in, is_google_jwt_valid, decode_jwt
from ..models.bearer_token import (
    get_bearer_token,
    generate_bearer_token,
    create_bearer_token,
)
from ..models.google_oauth_claim import get_google_oauth_claim, create_google_oauth_claim
from ..models.user import (
    get_user,
    make_user_inactive,
    parse_user_from_json,
    update_user,
    create_user)


class MeHandler(BaseBearerAuthHandler):
    @gen.coroutine
    def delete(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        user = yield make_user_inactive(user_id, conn)
        if user:
            self.set_status(200)
            self.write(user)
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not delete record")

    @gen.coroutine
    def get(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        user = yield get_user(user_id, conn)
        if user:
            self.set_status(200)
            self.write(user)
            raise Finish()
        else:
            raise HTTPError(404, reason="Could not find user")

    @gen.coroutine
    def patch(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        body = to_unicode(self.request.body)
        user = parse_user_from_json(body)
        if user is None:
            raise HTTPError(400, reason="Invalid JSON")
        new_user = yield update_user(user_id, user, conn)
        if new_user:
            self.set_status(200)
            self.write(new_user)
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not update record")

    @gen.coroutine
    def put(self):
        user_id = yield self.check_auth_for_user_id()
        conn = yield self.db_conn()
        body = to_unicode(self.request.body)
        user = parse_user_from_json(body)
        if user is None:
            raise HTTPError(400, reason="Invalid JSON")
        new_user = yield update_user(user_id, user, conn)
        if new_user:
            self.set_status(200)
            self.write(new_user)
            raise Finish()
        else:
            raise HTTPError(500, reason="Database could not update record")

    @gen.coroutine
    def check_auth_for_user_id(self):
        token = self.get_bearer_token()
        conn = yield self.db_conn()
        bearer_token = yield get_bearer_token(token, conn)
        if bearer_token is None:
            raise HTTPError(401, reason="Bearer token is invalid")

        return bearer_token.user_id


class MeByTokenHandler(BaseBearerAuthHandler):
    @gen.coroutine
    def post(self):
        # Get JWT from body and convert it to dictionary
        token = utf8(self.request.body)
        decoded_token = decode_jwt(token)
        google_certs = yield self.application.get_google_certs()
        if decoded_token is None:
            raise HTTPError(400, reason="Could not parse JWT")

        # Validate JWT is signed by google, issuer is correct and it's within exp
        is_iss = yield is_google_jwt_valid(token, decoded_token, google_certs)
        if not is_iss:
            raise HTTPError(401, reason="JWT signature invalid")

        # Check that the JWT is signed with our app as the aud
        is_aud = is_audience_in(decoded_token, self.application.client_ids)
        if not is_aud:
            raise HTTPError(401, reason="JWT aud is not valid")

        # Get the google user id from the sub field
        provider_uid = decoded_token.get('sub', None)
        if provider_uid is None:
            raise HTTPError(400, reason="JWT contained no sub field")

        # Map the provider_uid to the user_id
        conn = yield self.db_conn()
        claim = yield get_google_oauth_claim(provider_uid, conn)
        user = None
        if claim is None:
            # Create new user from JWT info
            user_id = uuid.uuid4()
            user = yield create_user(user_id, conn)
            if user is None:
                raise HTTPError(500, reason="Could not create new user")

            # Tie a new claim to this user
            claim = yield create_google_oauth_claim(provider_uid, user_id, conn)
            if claim is None:
                raise HTTPError(500, reason="Could not create new google OAuth claim")

        bearer_token = generate_bearer_token()
        new_bearer_token = yield create_bearer_token(bearer_token, claim.user_id, conn)

        if new_bearer_token is None:
            raise HTTPError(500, reason="Could not create bearer token")

        if user is None:
            user = yield get_user(claim.user_id, conn)

        if user is None:
            raise HTTPError(500, reason="Could not get user which must exist")

        token_container = {
            "type": "Bearer",
            "data": new_bearer_token.token,
        }
        me_by_token_container = {
            "token": token_container,
            "user": user._asdict()
        }

        self.set_status(200)
        self.write(me_by_token_container)
        raise Finish()


class UserHandler(BaseBearerAuthHandler):
    @gen.coroutine
    def delete(self, user_id=None):
        if user_id is None:
            raise HTTPError(405, reason="Cannot DELETE on collection")

    @gen.coroutine
    def get(self, user_id=None):
        if user_id is None:
            # FIXME: implement search for users
            raise HTTPError(405, reason="Cannot GET on collection")

    @gen.coroutine
    def patch(self, user_id=None):
        if user_id is None:
            raise HTTPError(405, reason="Cannot PATCH on collection")

    @gen.coroutine
    def post(self, user_id=None):
        if user_id:
            raise HTTPError(405, reason="Cannot POST with a user id")

    @gen.coroutine
    def put(self, user_id=None):
        if user_id is None:
            raise HTTPError(405, reason="Cannot PUT on collection")


class UsersHandler(BaseBearerAuthHandler):
    pass
