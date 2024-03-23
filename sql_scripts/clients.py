from models.base import Base
from utils.sqlalchemy import init_sqlite_db

session = init_sqlite_db(Base, path="/Volumes/workplace/Media/MediaApi/api/sqlite.db")
