from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

class Download(Base):

    __tablename__ = 'files'

    path = Column(String, primary_key=True)
    size = Column(Integer)
    type = Column(String)
    finished = Column(Boolean)

class Database:
    def __init__(self, db_url="sqlite:///database.db"):
        self.engine = create_engine(db_url, echo=True)
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)  # Thread-safe sessions

        # Automatically create tables
        Base.metadata.create_all(self.engine)

    def session(self):
        """Returns a new session (or an existing one if in the same thread)."""
        return self.Session()

    def close_session(self):
        """Closes the current session."""
        self.Session.remove()

# Singleton instance of Database
db = Database()