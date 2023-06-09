from datetime import datetime, timedelta

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, CHAR, Column, Date, DateTime, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, NUMERIC

from db_config import Session

Base = declarative_base()
