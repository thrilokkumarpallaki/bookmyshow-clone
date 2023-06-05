import json
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from log_util import get_logger
from db_config import redis_client as rc
from utils import create_response
from views.user import UserView

logger = get_logger(__name__)
auth_api = Blueprint('auth_api', __name__, url_prefix='/auth')


@auth_api.route('/signup', methods=['POST'])
def create_user():
    resp = {'msg': '', 'status_code': 2001, 'status': True}
    try:
        req_json = request.get_json()

        # Get user info from the request json
        first_name = req_json.get('first_name')
        last_name = req_json.get('last_name')
        email_id = req_json.get('email_id')
        password = req_json.get('password')
        phone = req_json.get('phone')

        new_user = UserView(first_name=first_name, last_name=last_name, email_id=email_id, password=password,
                            phone=phone)
        status, msg = new_user.save()
        resp['status'] = status
        resp['msg'] = msg
        resp['status_code'] = 5000 if not status else 2001
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['status'] = False
        resp['msg'] = 'An error occurred while creating the user'
        resp['status_code'] = 5000
    return create_response(resp)


@auth_api.route('/login', methods=['POST'])
def login_user():
    resp = {'msg': '', 'status_code': 2000, 'status': True}
    try:
        req_json = request.get_json()

        # Get auth details
        username = req_json.get('username')
        password = req_json.get('password')

        status, data = UserView.login(username, password)

        if not status:
            resp['msg'] = 'Invalid username/password. Please try again!'
            resp['status_code'] = 4000
            resp['status'] = status
        else:
            resp['data'] = data
            resp['msg'] = 'User authentication successful'
    except Exception as e:
        logger.exception(e, exc_info=True)
    return create_response(resp)


@auth_api.route('/logout', methods=['DELETE'])
@jwt_required()
def logout_user():
    resp = {'msg': 'user logged out successfully', 'status_code': 2000, 'status': True}
    try:
        r_key = get_jwt_identity()
        user_claims = json.loads(rc.get(r_key))
        if not user_claims:
            return
        else:
            jti = get_jwt()['jti']
            rc.set(jti, "", ex=3600)

            # remove claims from the cache
            rc.delete(r_key)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Unable to logout'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return resp


@auth_api.route('/deactivate-user', methods=['PUT'])
@jwt_required()
def deactivate_user():
    resp = {'msg': 'user deactivated successfully', 'status_code': 2000, 'status': True}
    try:
        user_claims = json.loads(rc.get(get_jwt_identity()))
        status, msg = UserView.deactivate_user(user_claims)
        resp['msg'] = msg
        resp['status'] = status
        resp['status_code'] = 5000 if not status else 2000
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Unable to deactivate user'
        resp['status'] = False
        resp['status_code'] = 5000
    return create_response(resp)


@auth_api.route('/forgot-password', methods=['POST'])
@jwt_required()
def forgot_password():
    pass


@auth_api.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    resp = {'msg': '', 'status_code': 2000, 'status': True}
    try:
        user_claims = json.loads(rc.get(get_jwt_identity()))
        req_json = request.get_json()

        old_password = req_json.get('old_password')
        new_password = req_json.get('new_password')

        if old_password == new_password:
            resp['msg'] = "New password cannot be same as old one's."
            resp['status_code'] = 4000
            resp['status'] = False
            return

        status, msg = UserView.change_password(user_claims, old_password, new_password)
        if not status:
            resp['msg'] = 'Password was not updated.'
            resp['status_code'] = 5000
            resp['status'] = False
        else:
            resp['msg'] = msg
    except Exception as e:
        logger.exception(e, exc_info=True)
    return create_response(resp)


@auth_api.route('/delete-user', methods=['DELETE'])
@jwt_required()
def delete_user():
    resp = {'msg': '', 'status_code': 2000, 'status': True}
    try:
        user_claims = json.loads(rc.get(get_jwt_identity()))
        status, msg = UserView.delete_user(user_claims)

        if not status:
            resp['msg'] = msg
            resp['status_code'] = 5000
            resp['status'] = False
        else:
            resp['msg'] = msg
    except Exception as e:
        logger.exception(e, exc_info=True)
    return create_response(resp)


@auth_api.route('/update-user', methods=['POST'])
@jwt_required()
def update_user():
    resp = {'msg': '', 'status_code': 2000, 'status': True}
    try:
        req_json = request.get_json()

        first_name = req_json.get('first_name')
        last_name = req_json.get('last_name')
        email_id = req_json.get('email_id')
        phone = req_json.get('phone')

        details = {'first_name': first_name, 'last_name': last_name, 'email_id': email_id, 'phone': phone}
        user_claims = json.loads(rc.get(get_jwt_identity()))
        status, msg = UserView.update_user(user_claims, **details)

        if not status:
            resp['msg'] = msg
            resp['status'] = False
            resp['status_code'] = 5000
        else:
            resp['msg'] = msg
    except Exception as e:
        logger.exception(e, exc_info=True)
    return create_response(resp)
