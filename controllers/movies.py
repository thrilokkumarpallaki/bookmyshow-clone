from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from utils import create_response
from log_util import get_logger
from views.movies import MoviesView, MovieStarView


logger = get_logger(__name__)
movies_api = Blueprint('movies_api', __name__, url_prefix='/movies')


@movies_api.route('/<int:movie_id>', methods=['GET'])
@jwt_required()
def get_movie(movie_id):
    resp = {'msg': 'Movie fetched successfully!', 'data': {}, 'status_code': 2000, 'status': True}
    try:
        resp = MoviesView.get_movie(movie_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong.'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return create_response(resp)


@movies_api.route('/list', methods=['GET'])
@jwt_required()
def list_movies():
    resp = {'msg': 'Movies fetched successfully!', 'data': [], 'status_code': 2000, 'status': True}
    try:
        req_args = request.args
        only_new = req_args.get('only_new')
        if only_new == 'all':
            only_new = None
        resp = MoviesView.list_movies(only_new)
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

        movie_obj = MoviesView(**new_movie_dict)
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
def add_movie_data(movie_id: int):
    resp = {'msg': 'Movie data added successfully!', 'status_code': 2001, 'status': True}
    try:
        movie_files = request.files
        resp = MoviesView.add_movie_data(movie_id, movie_files)
    except Exception as e:
        logger.exception(e, exc_info=True)
    finally:
        return create_response(resp)


@movies_api.route('/update-movie-data/<int:movie_id>', methods=['PUT'])
@jwt_required()
def update_movie_info(movie_id: int):
    resp = {'msg': 'Movie data updated successfully!', 'status_code': 2000, 'status': True}
    try:
        req_json = request.get_json()
        is_brand_new = req_json.get('is_brand_new', True)
        movie_start_date = req_json.get('movie_start_date')
        movie_end_date = req_json.get('movie_end_date')
        rating = req_json.get('rating')
        movie_new_info = {'is_brand_new': is_brand_new, 'movie_start_date': movie_start_date,
                          'movie_end_date': movie_end_date, 'rating': rating}
        resp = MoviesView.update_movie_info(movie_id, movie_new_info)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return create_response(resp)


@movies_api.route('/delete-movie/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def delete_movie(movie_id: int):
    resp = {'msg': 'Movie deleted successfully!', 'status_code': 2000, 'status': True}
    try:
        resp = MoviesView.delete_movie(movie_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return create_response(resp)


@movies_api.route('/moviestar/<int:star_id>', methods=['GET'])
@jwt_required()
def get_movie_star(star_id: int):
    resp = {'msg': 'Movie-Star fetched successfully!', 'data': {}, 'status_code': 2000, 'status': True}
    try:
        resp = MovieStarView.get_moviestar(star_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return create_response(resp)


@movies_api.route('/moviestars/<int:movie_id>', methods=['GET'])
@jwt_required()
def get_all_moviestars(movie_id: int):
    resp = {'msg': 'Movie-Stars fetched successfully!', 'data': [], 'status_code': 2000, 'status': True}
    try:
        resp = MovieStarView.get_all_moviestars(movie_id)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return create_response(resp)


@movies_api.route('/moviestar', methods=['POST'])
@jwt_required()
def create_moviestar():
    resp = {'msg': 'Movie star added successfully!', 'status_code': 2001, 'status': True}
    try:
        req_json = request.get_json()
        star_name = req_json.get('star_name')
        carrier_started_at = req_json.get('carrier_started_at')

        movie_star = MovieStarView(name=star_name, start_date=carrier_started_at)
        resp = movie_star.save()
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return resp


@movies_api.route('/moviestar', methods=['PUT'])
@jwt_required()
def update_moviestar():
    resp = {'msg': 'Movie star updated successfully!', 'status_code': 2000, 'status': True}
    try:
        req_json = request.get_json()
        star_id = req_json.get('star_id')
        star_name = req_json.get('star_name')
        carrier_started_at = req_json.get('carrier_started_at')
        total_movies = req_json.get('total_movies')
        if not star_id:
            resp['msg'] = 'Star Id is required.'
            resp['status'] = False
            resp['status_code'] = 4000
            return
        if not star_name and not carrier_started_at and not total_movies:
            resp['msg'] = 'No new data found.'
        resp = MovieStarView.update_moviestar(star_id=star_id, name=star_name, start_date=carrier_started_at,
                                              total_movies=total_movies)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return resp


@movies_api.route('/moviestar-relation', methods=['POST'])
@jwt_required()
def create_moviestar_relation():
    resp = {'msg': 'Movie-Star relationship created successfully!', 'status': True, 'status_code': 2001}
    try:
        req_json = request.get_json()
        star_ids = req_json.get('star_ids', [])
        movie_id = req_json.get('movie_id')

        if not star_ids or not movie_id:
            resp['msg'] = 'Star Mappings and Movie Id required.'
            resp['status'] = False
            resp['status_code'] = 4000
            return

        resp = MovieStarView.create_moviestar_relation(movie_id, star_ids)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return create_response(resp)


@movies_api.route('/moviestar-relation', methods=['DELETE'])
@jwt_required()
def remove_moviestar_relation():
    resp = {'msg': 'Movie star removed successfully!', 'status_code': 2000, 'status': True}
    try:
        req_json = request.get_json()
        star_ids = req_json.get('star_ids')
        movie_id = req_json.get('movie_id')

        resp = MovieStarView.remove_moviestar_relation(movie_id, star_ids)
    except Exception as e:
        logger.exception(e, exc_info=True)
        resp['msg'] = 'Something went wrong'
        resp['status_code'] = 5000
        resp['status'] = False
    finally:
        return create_response(resp)
