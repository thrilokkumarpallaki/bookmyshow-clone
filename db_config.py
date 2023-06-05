import os

from redis import Redis
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy import URL

url_object = URL(
  drivername="postgresql",
  database=os.environ['database'],
  username=os.environ['username'],
  password=os.environ['password'],
  host=os.environ['host'],
  port=int(os.environ['port']),
  query={}
)

# create db engine
engine = create_engine(url_object, pool_size=10)
Session = sessionmaker(bind=engine)

# Create Redis Client
redis_client = Redis()
