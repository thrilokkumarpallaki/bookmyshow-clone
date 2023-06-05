from log_util import get_logger
from . import *

logger = get_logger(__name__)


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(String(32), nullable=False, primary_key=True)
    first_name = Column('first_name', String(30), nullable=False)
    last_name = Column('last_name', String(30), nullable=False)
    email_id = Column('email_id', String(70), nullable=False)
    password = Column('password', String(60), nullable=False)
    phone = Column('phone', CHAR(10), nullable=True)
    email_verified = Column('email_verified', Boolean, default=False)
    is_active = Column('is_active', Boolean, default=True)
    is_deleted = Column('is_deleted', Boolean, default=False)
    last_login = Column('last_login', DateTime(timezone=True))
    created_at = Column('created_at', DateTime(timezone=True), default=datetime.utcnow())
    modified_at = Column('modified_at', DateTime(timezone=True))

    @staticmethod
    def create_user(**user_attrs):
        session = Session(expire_on_commit=True)
        status = True
        msg = 'User created successfully!'
        try:
            user_obj = UserModel(**user_attrs)
            user_obj.save()
        except Exception as e:
            logger.exception(e, exc_info=True)
            status = False
            msg = 'Something error occurred.'
        finally:
            session.close()
            return status, msg

    @staticmethod
    def get_user(user_id=None, username=None):
        session = Session(expire_on_commit=True)
        user_obj = None
        try:
            user_base_query = session.query(UserModel).filter(UserModel.is_active == True)
            if user_id:
                user_obj = user_base_query.filter(UserModel.id == user_id).first()
            else:
                user_obj = user_base_query.filter(UserModel.email_id == username).first()
        except Exception as e:
            logger.exception(e, exc_info=True)
        finally:
            session.close()
            return user_obj

    def save(self):
        session = Session(expire_on_commit=True)
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
        finally:
            session.close()

    @staticmethod
    def deactivate_user(user_id: str):
        status, msg = True, 'User deactivated successfully!'
        session = Session(expire_on_commit=True)
        try:
            session.query(UserModel).filter(UserModel.id == user_id).update({'is_active': False},
                                                                            synchronize_session=False)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            status, msg = False, 'An error occurred.'
        finally:
            session.close()
            return status, msg

    def update_user(self, **details: dict):
        status, msg = True, 'User updated successfully.'
        session = Session(expire_on_commit=True)
        try:
            # add modified_at field with updated timestamp
            details.update({'modified_at': datetime.utcnow()})
            for key, value in details.items():
                setattr(self, key, value)

            self.save()
        except Exception as e:
            logger.exception(e, exc_info=True)
            status = False
            msg = 'Unable to update user details.'
        finally:
            session.close()
            return status, msg
