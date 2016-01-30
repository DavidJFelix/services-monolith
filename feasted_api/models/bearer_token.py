from collections import namedtuple
from typing import Optional

from tornado import gen

BearerToken = namedtuple('BearerToken', [
    'token',
    'user_id',
])


@gen.coroutine
def create_bearer_token(token, user_id, db_conn) -> Optional[BearerToken]:
    pass


@gen.coroutine
def delete_bearer_token(token, db_conn) -> Optional[BearerToken]:
    pass


@gen.coroutine
def get_bearer_token(token) -> Optional[BearerToken]:
    pass
