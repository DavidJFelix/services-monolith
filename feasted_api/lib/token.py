import base64
import binascii
import time
from json import JSONDecodeError
from typing import Dict, Optional, List

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util.asn1 import DerSequence
from tornado import gen
from tornado.escape import json_decode, utf8


def decode_jwt(encoded_jwt: bytes) -> Optional[Dict]:
    try:
        _, b64_payload, _ = encoded_jwt.split(b".")
        payload_bytes = base64.b64decode(pad_b64string(b64_payload))
        payload_str = payload_bytes.decode()

        decoded_payload = json_decode(payload_str)
        return decoded_payload
    except (JSONDecodeError, binascii.Error, ValueError):
        return None


def is_after_issue_at(token: Dict) -> bool:
    token_iat = token.get('iat', None)
    try:
        issue_time = int(token_iat)
        now_time = int(time.time())
        return now_time > issue_time
    except ValueError:
        return False


def is_audience_in(token: Dict, audiences: List[str]) -> bool:
    token_aud = token.get('aud', None)
    return token_aud in audiences


def is_issuer_in(token: Dict, issuers: List[str]) -> bool:
    token_iss = token.get('iss', None)
    return token_iss in issuers


def is_within_expire_time(token: Dict) -> bool:
    token_exp = token.get('exp', None)
    try:
        expire_time = int(token_exp)
        now_time = int(time.time())
        return now_time < expire_time
    except ValueError:
        return False


def is_signed_by(token: bytes, certs: List[str]) -> bool:
    # TODO: FIXME: GOTTA TEST THIS. SERIOUSLY
    # FIXME FIXME FIXME
    header, payload, signature = token.split(b'.')
    message_to_sign = header + b'.' + payload
    digest = SHA256.new(message_to_sign)

    for cert in certs:
        cert = utf8(cert)
        pem_lines = cert.replace(b' ', b'').split()
        cert_der = base64.urlsafe_b64encode(b''.join(pem_lines[1:-1]).rstrip(b'='))
        cert_seq = DerSequence()
        cert_seq.decode(cert_der)

        tbs_seq = DerSequence()
        tbs_seq.decode(cert_seq[0])

        pub_key = RSA.importKey(tbs_seq[6])
        is_signed = PKCS1_v1_5.new(pub_key).verify(digest, signature)
        if is_signed:
            return True

    return False


def pad_b64string(b64string: bytes) -> bytes:
    return b64string + b'=' * (4 - len(b64string) % 4)


@gen.coroutine
def is_google_jwt_valid(encoded_token: bytes, decoded_token: Dict, certs: List[str]) -> bool:
    if not is_issuer_in(decoded_token, ['accounts.google.com', 'https://accounts.google.com']):
        return False

    if not is_within_expire_time(decoded_token):
        return False

    if not is_after_issue_at(decoded_token):
        return False

    if not is_signed_by(encoded_token, certs):
        return False

    return True
