from __future__ import annotations
from typing import Any

from pydantic import BaseModel, Extra, Field, validator

from . import *
from log_util import get_logger


logger = get_logger(__name__)


class TheaterScreenStatus:
    ACTIVE = 1
    NOT_ACTIVE = 2

    @classmethod
    def get_status(cls, status: int):
        if status == 1:
            return TheaterScreenStatus.ACTIVE
        elif status == 2:
            return TheaterScreenStatus.NOT_ACTIVE
        else:
            raise ValueError(f'Invalid Theater screen status: {status}')


class PydntTheaterModel(BaseModel):
    id: int = Field(None)
    name: str = Field(..., max_length=30)
    no_of_screens: int = Field(...)
    created_at: datetime = Field(None)
    modified_at: datetime = Field(None)
    is_deleted: bool = Field(default=False)

    @validator('name')
    def validate_theater_name(cls, field_value):
        if field_value == '' or field_value is None:
            raise ValueError('Theater name cannot be empty.')
        return field_value

    class Config:
        title = 'Theater'
        orm_mode = True
        extra = Extra.forbid
        anystr_strip_whitespace = True
        validate_assignment = True


class PydntTheaterScreenModel(BaseModel):
    id: int = Field(None)
    name: str = Field(..., max_length=10)
    theater_id: int = Field(...)
    status: int = Field(default=TheaterScreenStatus.ACTIVE)
    total_seats: int = Field(...)
    created_at: datetime = Field(None)
    modified_at: datetime = Field(None)
    is_deleted: bool = Field(default=False)

    class Config:
        title = 'Theater Screen'
        orm_mode = True
        extra = Extra.forbid
        arbitrary_types_allowed = True
        validate_assignment = True
        anystr_strip_whitespace = True


class PydntShowTimings(BaseModel):
    id: int = Field(None)
    screen_id: int = Field(...)
    movie_id: int = Field(...)
    theater_id: int = Field(...)
    show_starts_at: time = Field(...)
    is_currently_running: bool = Field(...)
    created_at: datetime = Field(None)
    modified_at: datetime = Field(None)

    class Config:
        title = 'Show Timings'
        orm_mode = True
        extra = Extra.forbid
        validate_assignment = True


class TheaterModel(Base):
    __tablename__ = 'theaters'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    no_of_screens = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())
    modified_at = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, default=False, nullable=False)

    @staticmethod
    def get_theaters_list() -> tuple[list[dict], str, bool]:
        status, msg = True, ''
        theaters_list = []
        session = Session()
        try:
            theater_objs = session.query(TheaterModel)\
                .filter(TheaterModel.is_deleted == False)\
                .order_by(TheaterModel.id).all()
            for theater_obj in theater_objs:
                theater = PydntTheaterModel.from_orm(theater_obj).dict()
                theaters_list.append(theater)
        except Exception as e:
            logger.exception(e, exc_info=True)
            msg = 'Something went wrong.'
            status = False
        finally:
            session.close()
            return theaters_list, msg, status

    @staticmethod
    def get_theater(theater_id: int) -> tuple[TheaterModel | None, str, bool]:
        status, msg = True, ''
        theater_obj = None
        session = Session()
        try:
            theater_obj = session.query(TheaterModel).filter(TheaterModel.id == theater_id)\
                .filter(TheaterModel.is_deleted == False).first()
        except Exception as e:
            logger.exception(e, exc_info=True)
            msg = 'Something went wrong.'
            status = False
        finally:
            session.close()
            return theater_obj, msg, status

    def save(self) -> tuple[str, bool]:
        status, msg = True, ''
        session = Session(expire_on_commit=True)
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            status = False
            msg = 'Something went wrong.'
        finally:
            session.close()
            return msg, status


class TheaterScreenModel(Base):
    __tablename__ = 'theater_screens'

    id = Column(Integer, primary_key=True)
    name = Column('screen_name', String(10), nullable=False)
    theater_id = Column(Integer, ForeignKey('theaters.id'), nullable=False)
    status = Column(Integer, nullable=False)
    total_seats = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())
    modified_at = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, default=False, nullable=False)

    def save(self) -> tuple[str, bool]:
        msg, status = '', True
        session = Session(expire_on_commit=True)
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            msg = 'Something went wrong.'
            status = False
        finally:
            session.close()
            return msg, status

    @staticmethod
    def get_theater_screen(screen_id: int) -> tuple[TheaterScreenModel, str, bool]:
        theater_screen_obj, msg, status = None, '', True
        session = Session()
        try:
            theater_screen_obj = session.query(TheaterScreenModel)\
                .filter(TheaterScreenModel.is_deleted == False)\
                .filter(TheaterScreenModel.id == screen_id).first()
        except Exception as e:
            logger.exception(e, exc_info=True)
            msg = 'Something went wrong.'
            status = False
        finally:
            session.close()
            return theater_screen_obj, msg, status

    @staticmethod
    def get_theater_screens(theater_id: int) -> tuple[list[dict], str, bool]:
        msg, status = '', True
        theater_screen_list = []
        session = Session()
        try:
            theater_screen_objs = session.query(TheaterScreenModel)\
                .filter(TheaterScreenModel.theater_id == theater_id)\
                .filter(TheaterScreenModel.is_deleted == False).all()

            for screen_obj in theater_screen_objs:
                screen_dict = PydntTheaterScreenModel.from_orm(screen_obj).dict()
                theater_screen_list.append(screen_dict)
        except Exception as e:
            logger.exception(e, exc_info=True)
            msg = 'Something went wrong.'
            status = False
        finally:
            session.close()
            return theater_screen_list, msg, status


class ShowTimingsModel(Base):
    __tablename__ = 'show_timings'

    id = Column(Integer, primary_key=True)
    screen_id = Column(Integer, ForeignKey('theater_screens.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    theater_id = Column(Integer, ForeignKey('theaters.id'), nullable=False)
    show_starts_at = Column(TIME, nullable=False)
    is_currently_running = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow())
    modified_at = Column(DateTime(timezone=True))

    __table_args__ = (UniqueConstraint(movie_id, theater_id, screen_id, show_starts_at,
                                       name='movie_theater_screen_show_at_ukey'),)

    def save(self):
        session = Session(expire_on_commit=True)
        msg, status = '', True
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logger.exception(e, exc_info=True)
            msg = 'Something went wrong.'
            status = False
        finally:
            session.close()
            return msg, status

    @staticmethod
    def get_showtiming(show_id):
        show_time_obj, msg, status = None, '', True
        session = Session()
        try:
            show_time_obj = session.query(ShowTimingsModel).filter(ShowTimingsModel.id == show_id).first()
        except Exception as e:
            logger.exception(e, exc_info=True)
            msg = 'Something went wrong.'
            status = False
        finally:
            session.close()
            return show_time_obj, msg, status

    @staticmethod
    def list_theater_screens(movie_id):
        status, msg = True, ''
        session = Session()
        theater_screen_list = []
        try:
            show_timing_objs = session.query(TheaterModel, TheaterScreenModel, ShowTimingsModel)\
                .join(TheaterModel, TheaterModel.id == ShowTimingsModel.theater_id)\
                .join(TheaterScreenModel, TheaterScreenModel.id == ShowTimingsModel.screen_id)\
                .filter(ShowTimingsModel.movie_id == movie_id)\
                .filter(ShowTimingsModel.is_currently_running == True).order_by(ShowTimingsModel.show_starts_at).all()

            theater_screen_dict: dict[str, Any] = {}
            for theater_obj, screen_obj, show_timing_obj in show_timing_objs:
                theater_dict = PydntTheaterModel.from_orm(theater_obj).dict()
                screen_dict = PydntTheaterScreenModel.from_orm(screen_obj).dict()
                show_timing_dict = PydntShowTimings.from_orm(show_timing_obj).dict()

                theater_id = str(show_timing_dict['theater_id'])
                screen_id = str(show_timing_dict['screen_id'])

                if theater_id not in theater_screen_dict:
                    theater_screen_dict[theater_id]: dict = theater_dict

                if 'screens' in theater_screen_dict[theater_id]:
                    if screen_id not in theater_screen_dict[theater_id]['screens']:
                        theater_screen_dict[theater_id]['screens'].update({screen_id: screen_dict})
                else:
                    theater_screen_dict[theater_id]['screens'] = {screen_id: screen_dict}

                if 'show_timings' in theater_screen_dict[theater_id]['screens'][screen_id]:
                    theater_screen_dict[theater_id]['screens'][screen_id]['show_timings'].append(show_timing_dict)
                else:
                    theater_screen_dict[theater_id]['screens'][screen_id]['show_timings'] = [show_timing_dict]

            for key, value in theater_screen_dict.items():
                theater = value.copy()
                theater['screens'] = []
                for key2, value2 in theater_screen_dict[key]['screens'].items():
                    theater['screens'].append(value2)
                theater_screen_list.append(theater)
        except Exception as e:
            logger.exception(e, exc_info=True)
            status = False
            msg = 'Something went wrong.'
        finally:
            session.close()
            return theater_screen_list, msg, status
