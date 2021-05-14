
from contextlib import contextmanager

from sqlalchemy import Column, create_engine
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from settings import Settings
from logger import LOG


Base = declarative_base()


class Timestamp(Base):
    __tablename__ = 'timestamp'
    id = Column(INTEGER, primary_key=True)
    last_sync_timestamp = Column(BIGINT)

    def __init__(self, timestamp):
        self.last_sync_timestamp = timestamp

    def __repr__(self):
        return f"Timestamp={self.last_sync_timestamp}"


def get_engine():
    connect_args = {}
    if Settings.SSL_MODE:
        connect_args={'sslmode': Settings.SSL_MODE}

    return create_engine(Settings.PG_HOST, connect_args=connect_args)


def load_db():
    engine = get_engine()
    Base.metadata.create_all(engine)


def session():
    # Return sqlalchemy session to database
    return Session(bind=get_engine(), expire_on_commit=False)


@contextmanager
def terminating_sn():
    # A context manager which closes session and db connections after use
    sn = session()
    try:
        yield sn
    finally:
        sn.close()
        sn.bind.dispose()

if __name__ == '__main__':
    LOG.info("creating tables...")
    load_db()