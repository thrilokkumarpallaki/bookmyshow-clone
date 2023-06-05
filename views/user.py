from uuid import uuid4
from datetime import datetime

from flask_jwt_extended import create_access_token, create_refresh_token
from flask_bcrypt import generate_password_hash, check_password_hash

from log_util import get_logger

from models.user_model import UserModel

logger = get_logger(__name__)


class UserView:
    def __init__(self, *, first_name: str, last_name: str, email_id: str, password: str, phone: str):
        self.user_id = uuid4().hex
        self.first_name = first_name
        self.last_name = last_name
        self.email_id = email_id
        self.password = password
        self.phone = phone

        # create password hash
        if password != '' and password is not None:
            self.pass_hash: str = generate_password_hash(password).decode('utf-8')
        else:
            raise ValueError('Password cannot be empty.')

    def save(self):
        try:
            _user_dict = {'id': self.user_id, 'first_name': self.first_name, 'last_name': self.last_name,
                          'email_id': self.email_id, 'password': self.pass_hash, 'phone': self.phone}
            status, msg = UserModel.create_user(**_user_dict)
        except Exception as e:
            logger.exception(e, exc_info=True)
            status = False
            msg = 'Something went wrong'
        return status, msg

    @staticmethod
    def login(username: str, password: str):
        status, msg = True, 'user login successful'
        try:
            current_user = UserModel.get_user(username=username)
            if current_user is not None:
                if not check_password_hash(current_user.password, password):
                    status = False
                    msg = 'Invalid username/password.'
                    return status, msg
                else:
                    identity = {
                        'r_key': uuid4().hex,
                        'id': current_user.id,
                        'email_id': current_user.email_id,
                        'first_name': current_user.first_name,
                        'last_name': current_user.last_name,
                        'phone': current_user.phone,
                        'is_active': current_user.is_active,
                        'is_deleted': current_user.is_deleted,
                        'is_verified': current_user.email_verified,
                        'last_login': current_user.last_login.strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # update last login status in db
                    current_user.last_login = datetime.utcnow()
                    current_user.save()

                    # create access token
                    access_token = create_access_token(identity, fresh=True)
                    refresh_token = create_refresh_token(identity)

                    # remove r_key from identity
                    identity.pop('r_key')

                    identity.update({'access_token': access_token, 'refresh_token': refresh_token})
                    msg = identity
            else:
                status, err_msg = False, 'Invalid username/password.'
        except Exception as e:
            logger.exception(e, exc_info=True)
            status, msg = False, 'An Error Occurred.'
        return status, msg

    @staticmethod
    def deactivate_user(user_claims: dict):
        try:
            user_id = user_claims.get('id')
            status, msg = UserModel.deactivate_user(user_id)
        except Exception as e:
            logger.exception(e, exc_info=True)
            status, msg = False, 'An Error Occurred.'
        return status, msg

    @staticmethod
    def change_password(user_claims: dict, old_pass: str, new_pass: str):
        status, msg = True, 'Password changed successfully'
        try:
            user_id = user_claims.get('id')

            # get user object
            user_obj = UserModel.get_user(user_id=user_id)

            # Check if old password is matching. Otherwise, return error.
            if not check_password_hash(user_obj.password, old_pass):
                status, msg = False, 'Invalid old password.'
                return
            else:
                new_pass_hash: str = generate_password_hash(new_pass).decode('utf-8')

                status, _ = user_obj.update_user(**{'password': new_pass_hash})
        except Exception as e:
            logger.exception(e, exc_info=True)
            status, msg = False, 'An Error Occurred.'
        finally:
            return status, msg

    @staticmethod
    def delete_user(user_claims: dict):
        status, msg = True, 'User deleted successfully'
        try:
            user_id = user_claims.get('id')
            user_obj = UserModel.get_user(user_id=user_id)

            if user_obj is not None:
                use_attrs = {'is_deleted': True}
                user_obj.update(use_attrs)
            else:
                status, msg = False, 'User does not exist'
        except Exception as e:
            logger.exception(e, exc_info=True)
            status = False
            msg = 'An error occurred.'
        return status, msg

    @staticmethod
    def update_user(user_claims: dict, **user_details):
        status, msg = True, 'User updated successfully'
        try:
            user_new_dict = {}
            for key, value in user_details.items():
                if value != '' and value is not None:
                    user_new_dict[key] = value

            user_id = user_claims.get('id')
            user_obj = UserModel.get_user(user_id=user_id)
            status, msg = user_obj.update_user(**user_new_dict)
        except Exception as e:
            logger.exception(e, exc_info=True)
            status, msg = False, 'An Error Occurred.'
        return status, msg
