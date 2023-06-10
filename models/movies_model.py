from __future__ import annotations
from typing import Any

import pytz
from pydantic import BaseModel, Field, Extra, PositiveFloat, PositiveInt, HttpUrl, validator

from . import *
from log_util import get_logger
from utils import generate_pre_signed_s3_urls

logger = get_logger(__name__)


class PydntMovieModel(BaseModel):
    id: int = Field(None)
    movie_name: str = Field(..., max_length=50)
    image_urls: list[HttpUrl] = Field(None, max_items=10)
    video_urls: list[HttpUrl] = Field(None, max_items=10)
    movie_rating: PositiveFloat = Field(..., exclusiveMaximum=10)
    is_brand_new: bool = Field(...)
    is_deleted: bool = Field(default=False)
    movie_start_date: datetime = Field(...)
    movie_end_date: datetime = Field(None, exclude=True)
    created_at: datetime = Field(None)
    modified_at: datetime = Field(None)

    class Config:
        orm_mode = True
        title = 'Movie'
        extras = Extra.forbid
        validate_assignment = True
        anystr_strip_whitespace = True

    @validator('movie_end_date')
    def validate_movie_start_end_date(cls, field_value, values):
        """ Validate movie start date is less than or equal to movie end date.
        If not. It raises a ValueError.
        """
        if field_value is None:
            return field_value

        movie_start_date = values.get('movie_start_date')
        movie_end_date = field_value.replace(tzinfo=pytz.UTC)

        if movie_start_date > movie_end_date:
            raise ValueError("movie_end_date cannot be less than movie_start_date.")
        return field_value


class PydntMovieStarModel(BaseModel):
    id: int = Field(None)
    star_name: str = Field(..., max_length=50)
    carrier_started_at: date = Field(...)
    total_movies: int = Field(default=0)
    image_urls: list[HttpUrl] = Field(None, max_items=10)
    created_at: datetime = Field(None)
    modified_at: datetime = Field(None)

    class Config:
        orm_mode = True
        title = 'Movie Star'
        extras = Extra.forbid
        validate_assignment = True
        anystr_strip_whitespace = True

    @validator('carrier_started_at', pre=True)
    def convert_carrier_start_date(cls, field_value):
        if isinstance(field_value, str):
            datetime.strptime(field_value, '%Y-%m-%d')
        return field_value

    @validator('carrier_started_at')
    def validate_carrier_started_at(cls, field_value):
        today = datetime.now().date()
        if field_value > today:
            raise ValueError('Carrier start date cannot be future date.')
        return field_value


class PydntMovieStarRelationModel(BaseModel):
    movie_id: int = Field(None, gt=0)
    star_ids: list[int] = Field(None, gt=0)

    class Config:
        title = 'Movie Star Mapping'
        extras = Extra.forbid
        validate_assignment = True

    @validator('star_ids', each_item=True)
    def validate_star_ids(cls, field_value, values):
        movie_id = values.get('movie_id')
        if not isinstance(field_value, int):
            raise ValueError(f'Invalid star id {field_value}. Cannot create relation with movie id {movie_id}.')


class MovieModel(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    movie_name = Column('name', String(50), nullable=False)
    image_urls = Column(ARRAY(String))
    video_urls = Column(ARRAY(String))
    movie_rating = Column('rating', NUMERIC)
    is_brand_new = Column(Boolean, nullable=False, default=True)
    movie_start_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow())
    movie_end_date = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())
    modified_at = Column(DateTime(timezone=True))

    @staticmethod
    def get_movie(movie_id: int) -> MovieModel | None:
        session = Session()
        movie_obj = None
        try:
            movie_obj = session.query(MovieModel).filter(MovieModel.id == movie_id).first()
        except Exception as e:
            logger.exception(e, exc_info=True)
        finally:
            session.close()
            return movie_obj

    def set_movie_end_date(self, override: bool = False) -> MovieModel:
        """
        This method helps to set a default movie_end_date, which is timedelta(days=7) with the
        help of self.movie_start_date. If self.movie_star_date is None it throws an error.
        Later user can modify with actual end date by calling the corresponding API.
        If it has value already in it and tries to set using this method it will throw
        ValueError.
        Unless override is true.
        :return: It returns the instance after updating the object.
        """

        if not override and self.movie_end_date:
            raise ValueError('movie_end_data already has a value assigned to it. Set override to True to '
                             'assign a new value.')
        td = timedelta(days=7)
        if self.movie_start_date is not None:
            if isinstance(self.movie_start_date, str):
                self.movie_start_date = datetime.strptime(self.movie_start_date, '%Y-%m-%dT%H:M:S')
            delta = self.movie_start_date + td
            self.movie_end_date = delta
        else:
            raise ValueError('In order to set movie_end_date, movie_start_data is required.')
        return self

    def save(self):
        """
        This method saves the object to database.
        It used in saving a new object, updating an existing object or soft deleting the object.
        :return:
        """
        session = Session(expire_on_commit=True)
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise Exception(e)
        finally:
            session.close()

    @staticmethod
    def list_movies(only_new: bool | None = True) -> tuple[list[dict] | Any, bool, str]:
        """
        This method list only movies which are marked as brand new. In other words
        it checks is_brand_new column and returns only records which are set to True.
        To return all the movies which are not brand-new pass only_new param as False.
        It also allows you to list all the movies including deleted ones from the db, if only_new is set to True.
        :param only_new: A boolean value to manipulate the list of movie records. Allowed values are
        `True`, `False` or `None`.
        :return: It returns list of Parsed pydantic movie model object, status, msg
        """
        session = Session()
        movies_list = []
        status = True
        msg = ''
        try:
            movies_base_query = session.query(MovieModel).filter(MovieModel.is_deleted == False).order_by(MovieModel.id)
            if only_new is not None:
                movies_objs = movies_base_query.filter(MovieModel.is_brand_new == only_new).all()
            else:
                movies_objs = movies_base_query.all()

            # Parse records into Pydantic Models
            for movie in movies_objs:
                movie_obj_dict = PydntMovieModel.from_orm(movie).dict()
                movie_obj_dict['image_urls'] = generate_pre_signed_s3_urls(movie_obj_dict['image_urls'])
                movie_obj_dict['video_urls'] = generate_pre_signed_s3_urls(movie_obj_dict['video_urls'])
                movies_list.append(movie_obj_dict)
        except Exception as e:
            logger.exception(e, exc_info=True)
            status = False
            msg = 'Something went wrong.'
        finally:
            session.close()
            return movies_list, status, msg

    def update_movie(self, **movie_details):
        try:
            for key, value in movie_details.items():
                setattr(self, key, value)
            self.save()
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise e.__class__(e)


class MovieStarModel(Base):
    __tablename__ = 'movie_stars'

    id = Column(Integer, primary_key=True)
    star_name = Column('name', String(50), nullable=False)
    carrier_started_at = Column(Date)
    total_movies = Column(Integer, default=0)
    image_urls = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())
    modified_at = Column(DateTime(timezone=True))

    def save(self):
        """
        This method saves movie star object to db.
        It also can be called if the movie star object got updated or deleted from the database.
        :return: It returns None.
        """
        session = Session(expire_on_commit=True)
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise e.__class__(e)
        finally:
            session.close()

    def update_movie_star(self, **star_details):
        """
        This method updates movie star details, using setattr function. It also raises
        error if something goes wrong.
        :param star_details: A dict of objects to update the movie star object.
        :return: It returns None.
        """
        try:
            for key, val in star_details:
                setattr(self, key, val)
            self.save()
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise e.__class__(e)

    @staticmethod
    def get_star(star_ids: list[int]) -> list[MovieStarsMapping] | MovieStarModel | None:
        """
        This method gets MovieStarModel object from the database using passed star_id.
        :param star_ids: Ids of the MovieStar objects
        :return: MovieStarModel Object
        """
        session = Session()
        star_objs = None
        try:
            star_objs = session.query(MovieStarModel).filter(MovieStarModel.id.in_(star_ids)).all()
            if len(star_objs) == 1:
                star_objs = star_objs[0]
            elif len(star_objs) == 0:
                star_objs = None
        except Exception as e:
            logger.exception(e, exc_info=True)
        finally:
            session.close()
            return star_objs

    @classmethod
    def get_all_moviestars(cls, movie_id):
        moviestar_list = []
        try:
            star_mappings = MovieStarsMapping.get_all_mappings(movie_id=movie_id)
            star_objs = cls.get_star(star_mappings)

            for star_obj in star_objs:
                star_dict = PydntMovieStarModel.from_orm(star_obj).dict()
                moviestar_list.append(star_dict)
        except Exception as e:
            logger.exception(e, exc_info=True)
        return moviestar_list


class MovieStarsMapping(Base):
    __tablename__ = 'movie_stars_mapping'

    star_id = Column(Integer, ForeignKey('movie_stars.id'), primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())
    modified_at = Column(DateTime(timezone=True))

    @staticmethod
    def get_all_mappings(movie_id: int) -> list[MovieStarsMapping | None]:
        session = Session()
        movie_star_mappings = []
        try:
            movie_star_mappings = session.query(MovieStarsMapping.star_id)\
                .filter(MovieStarsMapping.movie_id == movie_id).all()
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise e.__class__(e)
        finally:
            session.close()
            return movie_star_mappings

    @staticmethod
    def remove_movie_star_mappings(sids: list[int], mid: int):
        session = Session(expire_on_commit=True)
        try:
            session.query(MovieStarsMapping).filter(MovieStarsMapping.star_id.in_(sids)) \
                .filter(MovieStarsMapping.movie_id == mid).delete(synchronize_session=False)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise e.__class__(e)
        finally:
            session.close()

    def save(self):
        session = Session(expire_on_commit=True)
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise e.__class__(e)
        finally:
            session.close()

    @staticmethod
    def bulk_save(objs: list[MovieStarsMapping]):
        session = Session(expire_on_commit=True)
        try:
            session.bulk_save_objects(objs)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            raise e.__class__(e)
        finally:
            session.close()
