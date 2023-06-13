from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from views.theater import TheaterView, TheaterScreenView, ShowTimingsView

from log_util import get_logger
from utils import create_response


logger = get_logger(__name__)
theater_api = Blueprint('theater_api', __name__, url_prefix='/theaters')


@theater_api.route('/list', methods=['GET'])
@jwt_required()
def list_theaters():
    resp = {'msg': 'Theaters fetched successfully!', 'data': [], 'status': True, 'status_code': 2000}
    try:
        resp = TheaterView.get_theater_list()
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/<int:theater_id>', methods=['GET'])
@jwt_required()
def get_theater(theater_id: int):
    resp = {'msg': 'Theater fetched successfully!', 'data': {}, 'status': True, 'status_code': 2000}
    try:
        resp = TheaterView.get_theater(theater_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/', methods=['POST'])
@jwt_required()
def add_theater():
    resp = {'msg': 'Theater added successfully!', 'status': True, 'status_code': 2001}
    try:
        req_json = request.get_json()
        theater_name = req_json.get('theater_name')
        no_of_screens = req_json.get('no_of_screens')
        theater_obj = TheaterView(theater_name=theater_name, no_of_screens=no_of_screens)
        resp = theater_obj.save()
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/<int:theater_id>', methods=['PUT'])
@jwt_required()
def update_theater(theater_id: int):
    resp = {'msg': 'Theater updated successfully!', 'status': True, 'status_code': 2000}
    try:
        req_json = request.get_json()
        theater_name = req_json.get('theater_name')
        no_of_screens = req_json.get('no_of_screens')
        resp = TheaterView.update_theater(theater_id=theater_id, name=theater_name, no_of_screens=no_of_screens)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/<int:theater_id>', methods=['DELETE'])
@jwt_required()
def delete_theater(theater_id: int):
    resp = {'msg': 'Theater deleted successfully', 'status': True, 'status_code': 2000}
    try:
        resp = TheaterView.delete_theater(theater_id=theater_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/screen', methods=['POST'])
@jwt_required()
def add_theater_screen():
    resp = {'msg': 'Screen added to the theater successfully!', 'status': True, 'status_code': 2001}
    try:
        req_json = request.get_json()
        screen_name = req_json.get('screen_name')
        theater_id = req_json.get('theater_id')
        status = req_json.get('status')
        total_seats = req_json.get('total_seats')

        theater_screen_obj = TheaterScreenView(screen_name=screen_name, theater_id=theater_id, status=status,
                                               total_seats=total_seats)
        resp = theater_screen_obj.save()
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/screen/<int:screen_id>', methods=['PUT'])
@jwt_required()
def update_theater_screen(screen_id: int):
    resp = {'msg': 'Screen information updated successfully!', 'status': True, 'status_code': 2000}
    try:
        req_json = request.get_json()
        screen_name = req_json.get('screen_name')
        theater_id = req_json.get('theater_id')
        status = req_json.get('status')
        total_seats = req_json.get('total_seats')
        resp = TheaterScreenView.update_theater_screen(screen_id=screen_id, screen_name=screen_name,
                                                       theater_id=theater_id, status=status, total_seats=total_seats)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/screens/<int:theater_id>', methods=['GET'])
@jwt_required()
def list_theater_screens(theater_id: int):
    resp = {'msg': 'Theater screens fetched successfully!', 'data': [], 'status': True, 'status_code': 2000}
    try:
        resp = TheaterScreenView.theater_screen_list(theater_id=theater_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/screens/<int:screen_id>', methods=['DELETE'])
@jwt_required()
def delete_screen(screen_id):
    resp = {'msg': 'Theater screen deleted successfully!', 'status': True, 'status_code': 2000}
    try:
        resp = TheaterScreenView.delete_screen(screen_id=screen_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/screen/show-timings', methods=['POST'])
@jwt_required()
def add_show_timings():
    resp = {'msg': 'Show Timings added successfully!', 'status': True, 'status_code': 2001}
    try:
        req_json = request.get_json()
        theater_id = req_json.get('theater_id')
        screen_id = req_json.get('screen_id')
        movie_id = req_json.get('movie_id')
        show_starts_at = req_json.get('show_starts_at')
        is_currently_running = req_json.get('is_currently_running')
        showtiming_obj = ShowTimingsView(theater_id=theater_id, screen_id=screen_id, movie_id=movie_id,
                                         show_starts_at=show_starts_at, is_currently_running=is_currently_running)
        resp = showtiming_obj.save()
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/screen/show-timings/<int:show_timing_id>', methods=['PUT'])
@jwt_required()
def update_show_timings(show_timing_id: int):
    resp = {'msg': 'Show Timings updated successfully!', 'status': True, 'status_code': 2000}
    try:
        req_json = request.get_json()
        theater_id = req_json.get('theater_id')
        screen_id = req_json.get('screen_id')
        movie_id = req_json.get('movie_id')
        show_starts_at = req_json.get('show_starts_at')
        is_currently_running = req_json.get('is_currently_running')
        resp = ShowTimingsView.update_showtimings(show_timing_id=show_timing_id, theater_id=theater_id,
                                                  screen_id=screen_id, movie_id=movie_id, show_starts_at=show_starts_at,
                                                  is_currently_running=is_currently_running)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)


@theater_api.route('/list-screens/<int:movie_id>', methods=['GET'])
@jwt_required()
def theater_screens_by_movie(movie_id: int):
    resp = {'msg': 'Movie screens fetched successfully!', 'status': True, 'status_code': 2000}
    try:
        resp = ShowTimingsView.list_theater_screens(movie_id=movie_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status'] = False
        resp['status_code'] = 5000
    finally:
        return create_response(resp)
