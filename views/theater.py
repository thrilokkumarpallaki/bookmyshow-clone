from datetime import datetime, time
from typing import Any

from pydantic import ValidationError

from log_util import get_logger
from models.theater_model import (TheaterScreenStatus,
                                  PydntTheaterModel, PydntTheaterScreenModel, PydntShowTimings,
                                  TheaterModel, TheaterScreenModel, ShowTimingsModel)

logger = get_logger(__name__)


class TheaterView:
    def __init__(self, theater_name: str, no_of_screens: int):
        self.theater_name = theater_name
        self.no_of_screens = no_of_screens

    def save(self) -> dict:
        resp: dict[str, Any] = {'msg': 'Theater added successfully!', 'status': True, 'status_code': 2001}
        try:
            pydnt_theater_model = PydntTheaterModel(name=self.theater_name, no_of_screens=self.no_of_screens)

            theater_obj = TheaterModel(**pydnt_theater_model.dict(exclude_unset=True))
            msg, status = theater_obj.save()
            if not status:
                resp['msg'] = msg
                resp['status'] = False
                resp['status_code'] = 5000
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
    def get_theater_list() -> dict:
        resp = {'msg': 'Theaters fetched successfully!', 'data': [], 'status': True, 'status_code': 2000}
        try:
            theater_list, msg, status = TheaterModel.get_theaters_list()
            resp['data'] = theater_list
            if len(theater_list) == 0 and status:
                resp['msg'] = 'No Theaters Found.'
                resp['status'] = False
                resp['status_code'] = 2000
            if not status:
                resp['msg'] = 'Something went wrong.'
                resp['status'] = False
                resp['status_code'] = 5000
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def get_theater(theater_id: int) -> dict:
        resp: dict[str, Any] = {'msg': 'Theater fetched successfully!', 'data': {}, 'status': True, 'status_code': 2000}
        try:
            theater_obj, msg, status = TheaterModel.get_theater(theater_id)
            if not theater_obj and status:
                resp['msg'] = f'No Theater Found with Id: {theater_id}.'
                resp['status_code'] = 4000
                resp['status'] = False
                return resp
            if not status:
                resp['msg'] = 'Something went wrong.'
                resp['status'] = False
                resp['status_code'] = 5000
                return resp
            pydnt_theater_model = PydntTheaterModel.from_orm(theater_obj)
            theater_dict = pydnt_theater_model.dict()
            resp['data'] = theater_dict
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 5000
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def update_theater(theater_id: int, name: str | None, no_of_screens: int | None) -> dict:
        resp: dict[str, Any] = {'msg': 'Theater updated successfully!', 'status': True, 'status_code': 2000}
        try:
            theater_obj, msg, status = TheaterModel.get_theater(theater_id)
            if theater_obj is None and status:
                resp['msg'] = f'No Theaters present with id: {theater_id}.'
                resp['status'] = False
                resp['status_code'] = 4000

            pydnt_theater_model = PydntTheaterModel.from_orm(theater_obj)
            pydnt_theater_model.name = name
            pydnt_theater_model.no_of_screens = no_of_screens

            if pydnt_theater_model.name != theater_obj.name:
                theater_obj.name = pydnt_theater_model.name

            if pydnt_theater_model.no_of_screens != no_of_screens:
                theater_obj.no_of_screens = no_of_screens

            theater_obj.name = pydnt_theater_model.name
            theater_obj.no_of_screens = pydnt_theater_model.no_of_screens
            theater_obj.modified_at = datetime.utcnow()
            theater_obj.save()
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def delete_theater(theater_id: int):
        resp = {'msg': 'Theater deleted successfully', 'status': True, 'status_code': 2000}
        try:
            theater_obj, msg, status = TheaterModel.get_theater(theater_id)
            if theater_obj is not None:
                theater_obj.is_deleted = True
                theater_obj.save()
            elif status:
                resp['msg'] = f'No Theaters present with id: {theater_id}.'
                resp['status'] = False
                resp['status_code'] = 4000
            else:
                resp['msg'] = 'Something went wrong.'
                resp['status'] = False
                resp['status_code'] = 5000
        except Exception as e:
            logger.exception(e, exc_info=True)
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
        finally:
            return resp


class TheaterScreenView:
    def __init__(self, screen_name: str, theater_id: int, status: int, total_seats: int):
        self.screen_name = screen_name
        self.theater_id = theater_id
        self.status = status
        self.total_seats = total_seats

    def save(self) -> dict:
        resp: dict[str, Any] = {'msg': 'Screen added to the theater successfully!', 'status': True, 'status_code': 2001}
        try:
            pydnt_screen_model = PydntTheaterScreenModel(name=self.screen_name, theater_id=self.theater_id,
                                                         status=TheaterScreenStatus.get_status(self.status),
                                                         total_seats=self.total_seats)
            theater_screen_obj = TheaterScreenModel(**pydnt_screen_model.dict(exclude_unset=True))
            msg, status = theater_screen_obj.save()
            if not status:
                resp['msg'] = 'Something went wrong.'
                resp['status'] = False
                resp['status_code'] = 5000
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
    def update_theater_screen(screen_id: int, screen_name: str, theater_id: int, status: int, total_seats: int) -> dict:
        resp: dict[str, Any] = {'msg': 'Screen information updated successfully!', 'status': True, 'status_code': 2000}
        try:
            theater_screen_obj, msg, status_ = TheaterScreenModel.get_theater_screen(screen_id)
            pydnt_theater_screen_model = PydntTheaterScreenModel.from_orm(theater_screen_obj)
            pydnt_theater_screen_model.name = screen_name
            pydnt_theater_screen_model.theater_id = theater_id
            pydnt_theater_screen_model.status = TheaterScreenStatus.get_status(status)
            pydnt_theater_screen_model.total_seats = total_seats

            if theater_screen_obj.name != pydnt_theater_screen_model.name:
                theater_screen_obj.name = pydnt_theater_screen_model.name
            if theater_screen_obj.theater_id != pydnt_theater_screen_model.theater_id:
                theater_screen_obj.theater_id = pydnt_theater_screen_model.theater_id
            if theater_screen_obj.status != pydnt_theater_screen_model.status:
                theater_screen_obj.status = pydnt_theater_screen_model.status
            if theater_screen_obj.total_seats != pydnt_theater_screen_model.total_seats:
                theater_screen_obj.total_seats = pydnt_theater_screen_model.total_seats
            theater_screen_obj.modified_at = datetime.utcnow()
            theater_screen_obj.save()
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def theater_screen_list(theater_id: int):
        resp: dict[str, Any] = {'msg': 'Theater screens fetched successfully!', 'data': [], 'status': True,
                                'status_code': 2000}
        try:
            theater_screen_list, msg, status = TheaterScreenModel.get_theater_screens(theater_id)
            resp['data'] = theater_screen_list
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def delete_screen(screen_id: int):
        resp = {'msg': 'Theater screen deleted successfully!', 'status': True, 'status_code': 2000}
        try:
            theater_screen_obj, msg, status = TheaterScreenModel.get_theater_screen(screen_id=screen_id)
            if theater_screen_obj is None and status:
                resp['msg'] = f'No Theater Screen present with id: {screen_id}'
                resp['status'] = False
                resp['status_code'] = 4000
                return resp
            if not status:
                resp['msg'] = 'Something went wrong.'
                resp['status'] = False
                resp['status_code'] = 5000
                return resp
            theater_screen_obj.is_deleted = True
            theater_screen_obj.save()
        except Exception as e:
            logger.exception(e, exc_info=True)
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
        finally:
            return resp


class ShowTimingsView:
    def __init__(self, theater_id: int, screen_id: int, movie_id: int, show_starts_at: time,
                 is_currently_running: bool):
        self.theater_id = theater_id
        self.screen_id = screen_id
        self.movie_id = movie_id
        self.show_starts_at = show_starts_at
        self.is_currently_running = is_currently_running

    def save(self) -> dict:
        resp: dict[str, Any] = {'msg': 'Show Timings added successfully!', 'status': True, 'status_code': 2001}
        try:
            pydnt_show_timings_model = PydntShowTimings(theater_id=self.theater_id, screen_id=self.screen_id,
                                                        movie_id=self.movie_id, show_starts_at=self.show_starts_at,
                                                        is_currently_running=self.is_currently_running)
            showtimings_obj = ShowTimingsModel(**pydnt_show_timings_model.dict(exclude_unset=True))
            msg, status = showtimings_obj.save()
            if not status:
                resp['msg'] = msg
                resp['status'] = False
                resp['status_code'] = 5000
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def update_showtimings(show_timing_id: int, theater_id: int, screen_id: int, movie_id: int, show_starts_at: time,
                           is_currently_running: bool) -> dict:
        resp: dict[str, Any] = {'msg': 'Show Timings updated successfully!', 'status': True, 'status_code': 2000}
        try:
            showtimings_obj, msg, status = ShowTimingsModel.get_showtiming(show_timing_id)
            if not status:
                resp['msg'] = msg
                resp['status'] = False
                resp['status_code'] = 5000
                return resp
            elif not showtimings_obj and status:
                resp['msg'] = f'No Showtimings present with id: {show_timing_id}.'
                resp['status'] = False
                resp['status_code'] = 4000
                return resp

            pydnt_showtimings_model = PydntShowTimings.from_orm(showtimings_obj)
            pydnt_showtimings_model.theater_id = theater_id
            pydnt_showtimings_model.screen_id = screen_id
            pydnt_showtimings_model.movie_id = movie_id
            pydnt_showtimings_model.show_starts_at = show_starts_at
            pydnt_showtimings_model.is_currently_running = is_currently_running

            if pydnt_showtimings_model.screen_id != showtimings_obj.screen_id:
                showtimings_obj.screen_id = pydnt_showtimings_model.screen_id
            if pydnt_showtimings_model.movie_id != showtimings_obj.movie_id:
                showtimings_obj.movie_id = showtimings_obj.movie_id
            if pydnt_showtimings_model.show_starts_at != showtimings_obj.show_starts_at:
                showtimings_obj.show_starts_at = pydnt_showtimings_model.show_starts_at
            if pydnt_showtimings_model.is_currently_running != showtimings_obj.is_currently_running:
                showtimings_obj.is_currently_running = pydnt_showtimings_model.is_currently_running
            showtimings_obj.modified_at = datetime.utcnow()
            msg, status = showtimings_obj.save()
            if not status:
                resp['msg'] = msg
                resp['status'] = False
                resp['status_code'] = 5000
        except ValidationError as ve:
            resp['msg'] = ve.errors()
            resp['status'] = False
            resp['status_code'] = 4000
        except Exception as e:
            resp['msg'] = 'Something went wrong.'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp

    @staticmethod
    def list_theater_screens(movie_id: int):
        resp = {'msg': 'Movie screens fetched successfully!', 'data': [], 'status': True, 'status_code': 2000}
        try:
            theater_screen_list, msg, status = ShowTimingsModel.list_theater_screens(movie_id)
            if len(theater_screen_list) == 0 and status:
                resp['msg'] = 'No Theaters Found!'
                return resp
            if not status:
                resp['msg'] = msg
                resp['status'] = True
                resp['status_code'] = 5000
                return resp
            resp['data'] = theater_screen_list
        except Exception as e:
            resp['msg'] = 'Something went wrong'
            resp['status'] = False
            resp['status_code'] = 5000
            logger.exception(e, exc_info=True)
        finally:
            return resp
