from flask import Blueprint, request

from log_util import get_logger


logger = get_logger(__name__)
payment_api = Blueprint('payment_api', __name__)


@payment_api.route('/continue-payment', methods=['POST'])
def get_seats_info():
    resp = {''}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)
