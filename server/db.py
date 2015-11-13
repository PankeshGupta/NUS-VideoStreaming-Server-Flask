from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import DB_URI

session_factory = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI, isolation_level="READ UNCOMMITTED"))
