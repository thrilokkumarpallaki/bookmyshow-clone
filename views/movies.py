from datetime import datetime
from typing import Any

from pydantic import ValidationError
from werkzeug.datastructures import ImmutableMultiDict

from models.movies_model import (MovieModel, MovieStarModel, MovieStarsMapping, PydntMovieModel, PydntMovieStarModel,
                                 PydntMovieStarRelationModel)
from log_util import get_logger
from utils import parse_movie_file_data, generate_pre_signed_s3_urls

logger = get_logger(__name__)


class MoviesView:
    def __init__(self, movie_name: str,
                 rating: float,
                 is_brand_new: bool,
                 movie_start_date: datetime,
                 movie_end_date: datetime):
        self.name = movie_name
        self.rating = rating
        self.is_brand_new = is_brand_new
        self.movie_start_date = movie_start_date
        self.movie_end_date = movie_end_date

        self.image_urls = []
        self.video_urls = []

    def save(self) -> dict:
        resp = {'msg': 'Movie added successfully!', 'status': True, 'status_code': 2001}
        try:
            pydnt_movie_model_obj = PydntMovieModel(movie_name=self.name,
                                                    image_urls=self.image_urls,
                                                    video_urls=self.video_urls,
                                                    movie_rating=self.rating,
                                                    is_brand_new=self.is_brand_new,
                                                    movie_start_date=self.movie_start_date,
                                                    movie_end_date=self.movie_end_date)
            movie_dict = pydnt_movie_model_obj.dict(exclude_unset=True)
            movie_obj = MovieModel(**movie_dict)

            if not self.movie_end_date:
                movie_obj.set_movie_end_date()
            movie_obj.save()
        except ValidationError as ve:
            logger.exception(ve, exc_info=True)
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
        return resp

    @staticmethod
    def get_movie(movie_id: int) -> dict:
        resp = {'msg': 'Movie fetched successfully!', 'data': {}, 'status_code': 2000, 'status': True}
        try:
            movie_obj = MovieModel.get_movie(movie_id)
            pydnt_movie_dict = PydntMovieModel.from_orm(movie_obj)
            movie_dict = pydnt_movie_dict.dict()

            movie_dict['image_urls'] = generate_pre_signed_s3_urls(movie_dict['image_urls'])
            movie_dict['video_urls'] = generate_pre_signed_s3_urls(movie_dict['video_urls'])
            resp['data'] = movie_dict
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status_code'] = 5000
            resp['status'] = False
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def list_movies(only_new: bool | None = True) -> dict:
        resp = {'msg': 'Movies fetched successfully!', 'data': [], 'status_code': 2000, 'status': True}
        try:
            movies_list, status, msg = MovieModel.list_movies(only_new)
            if not status:
                raise ValueError(msg)
            resp['data'] = movies_list
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status_code'] = 5000
            resp['status'] = False
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def add_movie_data(movie_id: int, media_files: ImmutableMultiDict) -> dict | None:
        resp: dict[str, Any] = {'msg': 'Movie media added successfully!', 'status_code': 2000, 'status': True}
        try:
            movie_obj = MovieModel.get_movie(movie_id)
            if movie_obj is not None:
                movie_name = movie_obj.movie_name
                s3_object_urls_dict = parse_movie_file_data(media_files, movie_name)

                # Parse data as pydantic model
                pydnt_movie_model = PydntMovieModel.from_orm(movie_obj)
                pydnt_movie_model.image_urls = s3_object_urls_dict['image_urls']
                pydnt_movie_model.video_urls = s3_object_urls_dict['video_urls']

                movie_obj.image_urls = pydnt_movie_model.image_urls
                movie_obj.video_urls = pydnt_movie_model.video_urls
                movie_obj.save()
            else:
                resp['status'] = False
                resp['msg'] = 'Movie does not exist!'
                resp['status_code'] = 4000
                return
        except ValidationError as ve:
            logger.exception(ve, exc_info=True)
            resp['status'] = False
            resp['status_code'] = 4000
            resp['msg'] = ve.errors()
        except Exception as e:
            logger.exception(e, exc_info=True)
            resp['status'] = False
            resp['msg'] = 'Something went wrong.'
            resp['status_code'] = 5000
        finally:
            return resp

    @staticmethod
    def update_movie_info(movie_id: int, movie_info: dict) -> dict:
        resp: dict[str, Any] = {'msg': 'Movie updated successfully', 'status_code': 2000, 'status': True}
        try:
            # Get movie object
            movie_obj = MovieModel.get_movie(movie_id)

            # Parse movie object into Pydnt Movie Model.
            pydnt_movie_model = PydntMovieModel.from_orm(movie_obj)
            if movie_info['is_brand_new'] is not None:
                pydnt_movie_model.is_brand_new = movie_info['is_brand_new']
            if movie_info['movie_start_date'] is not None:
                pydnt_movie_model.movie_start_date = movie_info['movie_start_date']
            if movie_info['movie_end_date'] is not None:
                pydnt_movie_model.movie_end_date = movie_info['movie_end_date']
            if movie_info['rating'] is not None:
                pydnt_movie_model.movie_rating = movie_info['rating']

            movie_obj.is_brand_new = pydnt_movie_model.is_brand_new
            movie_obj.movie_start_date = pydnt_movie_model.movie_start_date
            movie_obj.movie_end_date = pydnt_movie_model.movie_end_date
            movie_obj.movie_rating = pydnt_movie_model.movie_rating

            movie_obj.modified_at = pydnt_movie_model.modified_at = datetime.utcnow()
            movie_obj.save()
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
            logger.exception(ve, exc_info=True)
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def delete_movie(movie_id) -> dict:
        resp = {'msg': 'Movie deleted successfully!', 'status': True, 'status_code': 2000}
        try:
            movie_obj = MovieModel.get_movie(movie_id)
            if movie_obj is not None:
                if not movie_obj.is_deleted:
                    movie_obj.is_deleted = True
                    movie_obj.save()
                else:
                    resp['msg'] = 'Movie already deleted!'
            else:
                resp['msg'] = 'Movie does not exist!'
                resp['status'] = False
                resp['status_code'] = 4000
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp


class MovieStarView:
    def __init__(self, name: str, start_date: str):
        self.star_name = name
        self.start_date = start_date

    def save(self) -> dict:
        resp: dict[str, Any] = {'msg': 'Movie star created successfully!', 'status': True, 'status_code': 2001}
        try:
            pydnt_movie_star = PydntMovieStarModel(star_name=self.star_name, carrier_started_at=self.start_date)
            movie_star_dict = pydnt_movie_star.dict(exclude_unset=True)
            movie_star_obj = MovieStarModel(**movie_star_dict)
            movie_star_obj.save()
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
            logger.exception(ve, exc_info=True)
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def update_moviestar(star_id: int, name: str, start_date: str, total_movies: int):
        resp: dict[str, Any] = {'msg': 'Movie star updated successfully!'}
        try:
            moviestar_obj = MovieStarModel.get_star([star_id])
            pydnt_moviestar_obj = PydntMovieStarModel.from_orm(moviestar_obj)
            if name is not None:
                pydnt_moviestar_obj.star_name = name
            if start_date is not None:
                pydnt_moviestar_obj.carrier_started_at = start_date
            if total_movies is not None:
                pydnt_moviestar_obj.total_movies = total_movies

            if moviestar_obj.total_movies != pydnt_moviestar_obj.total_movies:
                moviestar_obj.total_movies = pydnt_moviestar_obj.total_movies
            if moviestar_obj.star_name != pydnt_moviestar_obj.star_name:
                moviestar_obj.star_name = pydnt_moviestar_obj.star_name
            if moviestar_obj.carrier_started_at != pydnt_moviestar_obj.carrier_started_at:
                moviestar_obj.carrier_started_at = pydnt_moviestar_obj.carrier_started_at
            moviestar_obj.save()
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
            logger.exception(ve, exc_info=True)
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def create_moviestar_relation(movie_id: int, star_ids: list[int]) -> dict:
        resp: dict[str, Any] = {'msg': 'Movie-Star relationship created successfully!', 'status': True,
                                'status_code': 2001}
        movie_star_mapping_obj: list[MovieStarsMapping] = []
        try:
            PydntMovieStarRelationModel(movie_id=movie_id, star_ids=star_ids)
            for star_id in star_ids:
                obj_ = MovieStarsMapping(star_id=star_id, movie_id=movie_id)
                movie_star_mapping_obj.append(obj_)

            MovieStarsMapping.bulk_save(movie_star_mapping_obj)
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
            logger.exception(ve, exc_info=True)
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def remove_moviestar_relation(movie_id, star_ids: list[int]) -> dict:
        resp: dict[str, Any] = {'msg': 'Movie-Star relationship removed successfully!', 'status': False,
                                'status_code': 2000}
        try:
            PydntMovieStarRelationModel(movie_id=movie_id, star_ids=star_ids)
            MovieStarsMapping.remove_movie_star_mappings(star_ids, movie_id)
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
            logger.exception(ve, exc_info=True)
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def get_moviestar(star_id: int):
        resp = {'msg': 'Movie-Star fetched successfully!', 'data': {}, 'status_code': 2000, 'status': True}
        try:
            star_obj = MovieStarModel.get_star([star_id])
            if star_obj is not None:
                pydnt_star_obj = PydntMovieStarModel.from_orm(star_obj)
                resp['data'] = pydnt_star_obj.dict()
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def get_all_moviestars(movie_id: int):
        resp = {'msg': 'Movie-Stars fetched successfully!', 'data': [], 'status_code': 2000, 'status': True}
        try:
            resp['data'] = MovieStarModel.get_all_moviestars(movie_id=movie_id)
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp
