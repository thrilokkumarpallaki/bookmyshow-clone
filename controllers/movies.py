from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from log_util import get_logger
from db_config import redis_client as rc


logger = get_logger(__name__)
movies_api = Blueprint('movies_api', __name__, url_prefix='/movies')


@movies_api.route('/', methods=['GET'])
@jwt_required()
def list_movies():
    resp = {'msg': 'Movies fetched successfully!', 'data': [], 'status_code': 2000, 'status': True}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)


@movies_api.route('/add-movie', methods=['POST'])
@jwt_required()
def add_movie():
    resp = {'msg': 'New movie added successfully!', 'status_code': 2001, 'status': True}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)


@movies_api.route('/add-movie-data', methods=['POST'])
@jwt_required()
def add_movie_data():
    resp = {'msg': 'Movie data added successfully!', 'status_code': 2001, 'status': True}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)


@movies_api.route('/update-movie-data', methods=['PUT'])
@jwt_required()
def update_movie_data():
    resp = {'msg': 'Movie data updated successfully', 'status_code': 2000, 'status': True}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)


@movies_api.route('/create-movie-star', methods=['POST'])
@jwt_required()
def create_movie_star():
    resp = {'msg': 'Movie star added successfully!', 'status_code': 2001, 'status': True}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)


@movies_api.route('/update-movie-star', methods=['PUT'])
@jwt_required()
def update_movie_star():
    resp = {'msg': 'Movie star updated successfully!', 'status_code': 2000, 'status': True}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)


@movies_api.route('/remove-star', methods=['DELETE'])
@jwt_required()
def remove_movie_star():
    resp = {'msg': 'Movie star removed successfully!', 'status_code': 2000, 'status': True}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)


