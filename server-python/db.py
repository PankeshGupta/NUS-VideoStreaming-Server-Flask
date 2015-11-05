
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from settings import DB_URI

Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI, isolation_level="READ UNCOMMITTED"))
session = scoped_session(Session)

