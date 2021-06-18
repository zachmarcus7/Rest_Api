# Zach Marcus
# CS 493, Cloud Application Development
# Final Project
# ================================================================
# This file contains all the functions for authentication with 
# auth0 and JWT handling.
# ================================================================
from six.moves.urllib.request import urlopen
from authlib.integrations.flask_client import OAuth
from jose import jwt
import json
import constants


class AuthError(Exception):
    def __init__(self, error, status_code):
        """
        This is used in conjunction with the verify_jwt function.
        Taken from the auth0 documentation.
        """
        self.error = error
        self.status_code = status_code


def register_auth0(oauth):
    """
    This is used to authenticate the user with the specified 
    auth0 account.
    """
    auth0 = oauth.register(
        'auth0',
        client_id = constants.CLIENT_ID,
        client_secret = constants.CLIENT_SECRET,
        api_base_url = "https://" + constants.DOMAIN,
        access_token_url = "https://" + constants.DOMAIN + "/oauth/token",
        authorize_url = "https://" + constants.DOMAIN + "/authorize",
        client_kwargs={
            'scope': 'openid profile email',
        },
    )
    return auth0


def verify_jwt(request):
    """
    Checks if the JWT of the current user is actually in auth0.
    """
    auth_header = request.headers['Authorization'].split();
    token = auth_header[1]
    
    jsonurl = urlopen("https://"+ constants.DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        return "error"
    if unverified_header["alg"] == "HS256":
        return "error"
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=constants.ALGORITHMS,
                audience=constants.CLIENT_ID,
                issuer="https://"+ constants.DOMAIN+"/"
            )
        except jwt.ExpiredSignatureError:
            return "error"
        except jwt.JWTClaimsError:
            return "error"
        except Exception:
            return "error"
        return payload
    else:
        return "error"
