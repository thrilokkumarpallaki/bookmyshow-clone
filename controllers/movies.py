from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from utils import create_response
from log_util import get_logger
from db_config import redis_client as rc

from views.movies import Movies


logger = get_logger(__name__)
movies_api = Blueprint('movies_api', __name__, url_prefix='/movies')


@movies_api.route('/list', methods=['GET'])
@jwt_required()
def list_movies():
    resp = {'msg': 'Movies fetched successfully!', 'data': [], 'status_code': 2000, 'status': True}
    try:
        resp = Movies.list_movies()
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return create_response(resp)


@movies_api.route('/add-movie', methods=['POST'])
@jwt_required()
def add_movie():
    resp = {'msg': 'New movie added successfully!', 'status_code': 2001, 'status': True}
    try:
        req_json = request.get_json()

        name = req_json.get('movie_name')
        rating = req_json.get('rating')
        is_brand_new = req_json.get('is_brand_new', True)
        movie_start_date = req_json.get('movie_start_date')
        movie_end_date = req_json.get('movie_end_date')

        new_movie_dict = {'movie_name': name, 'rating': rating,
                          'is_brand_new': is_brand_new, 'movie_start_date': movie_start_date,
                          'movie_end_date': movie_end_date}

        movie_obj = Movies(**new_movie_dict)
        resp = movie_obj.save()
    except Exception as e:
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
        logger.exception(e, exc_info=True)
    finally:
        return create_response(resp)


@movies_api.route('/add-movie-data/<int:movie_id>', methods=['POST'])
@jwt_required()
def add_movie_data(movie_id):
    resp = {'msg': 'Movie data added successfully!', 'status_code': 2001, 'status': True}
    try:
        movie_files = request.files
        Movies.add_movie_data(movie_id, movie_files)
    except Exception as e:
        logger.exception(e, exc_info=True)
    finally:
        return create_response(resp)


@movies_api.route('/update-movie-data', methods=['PUT'])
@jwt_required()
def update_movie_data():
    resp = {'msg': 'Movie data updated successfully!', 'status_code': 2000, 'status': True}
    try:
        pass
    except Exception as e:
        logger.exception(e, exc_info=True)


@movies_api.route('/delete-movie', methods=['DELETE'])
def delete_movie():
    resp = {'msg': 'Movie deleted successfully!', 'status_code': 2000, 'status': True}
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
