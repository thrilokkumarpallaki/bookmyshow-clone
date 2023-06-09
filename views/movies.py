from datetime import datetime
from pydantic import ValidationError
from models.movies_model import MovieModel, MovieStar, MovieStarsMapping, PydntMovieModel, PydntMovieStarModel
from log_util import get_logger
from utils import parse_movie_file_data

logger = get_logger(__name__)


class Movies:
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

    def save(self):
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
    def list_movies(only_new: bool = True):
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
    def add_movie_data(movie_id, media_files):
        status, msg = True, 'Movie data added successfully!'
        try:
            movie_obj = MovieModel.get_movie(movie_id)
            if movie_obj is not None:
                movie_name = movie_obj.movie_name
                s3_object_urls_dict = parse_movie_file_data(media_files, movie_name)

                # Parse data as pydantic model
                pydnt_movie_model = PydntMovieModel.from_orm(movie_obj)
                pydnt_movie_model.image_urls = s3_object_urls_dict['image_urls']
                pydnt_movie_model.video_urls = s3_object_urls_dict['video_urls']

                movie_obj.image_urls = s3_object_urls_dict['image_urls']
                movie_obj.video_urls = s3_object_urls_dict['video_urls']
                movie_obj.save()
            else:
                status = False
                msg = 'Movie does not exist!'
                return
        except ValidationError as ve:
            logger.exception(ve, exc_info=True)
            status = False
            msg = ve.errors()
        except Exception as e:
            logger.exception(e, exc_info=True)
            status = False
            msg = 'Something went wrong.'
        finally:
            return status, msg
