from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, CHAR, Column, DateTime, Integer, String, ForeignKey

from db_config import Session

Base = declarative_base()