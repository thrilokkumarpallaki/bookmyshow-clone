import os
import json

from flask import Flask
from flask_jwt_extended import JWTManager

from log_util import get_logger
from db_config import redis_client as rc

from controllers import *


logger = get_logger(__name__)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ['secret_key']
app.config['JWT_HEADER_NAME'] = os.environ['jwt_header_name']
app.config['JWT_HEADER_TYPE'] = ''
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400

jwt = JWTManager(app)

# Register controllers
app.register_blueprint(auth_api)


@jwt.user_identity_loader
def user_claims(identity):
    r_key = identity.get('r_key')

    try:
        rc.set(r_key, json.dumps(identity), ex=3600)
    except Exception as e:
        logger.exception(e, exc_info=True)
    return r_key


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
    jti = jwt_payload['jti']
    token = rc.get(jti)

    return token is not None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
