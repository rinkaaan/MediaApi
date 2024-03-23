import os
from typing import Union

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def sanitize_dict(d, fields):
    return {k: v for k, v in d.items() if k in fields}


def sanitize_body(model, body, fields=None):
    fields = fields or model.editable_fields
    return sanitize_dict(body, fields)


def deserialize_body(model, body, fields=None):
    body = sanitize_body(model, body, fields)
    return model(**body)


def init_postgres_db(base, host="127.0.0.1"):
    url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=host,
        port=5432,
        database="postgres"
    )

    engine = create_engine(url)
    session = scoped_session(
        sessionmaker(autoflush=False, bind=engine)
    )
    base.query = session.query_property()
    base.metadata.create_all(bind=engine)
    return session


def init_sqlite_db(base, path="sqlite.db"):
    engine = create_engine(f"sqlite:///{path}", echo=True)
    session = scoped_session(
        sessionmaker(autoflush=True, bind=engine)
    )
    base.query = session.query_property()
    base.metadata.create_all(bind=engine)
    return session


class SessionManager:
    def __init__(self, base):
        self.base = base
        self.session: Union[scoped_session, None] = None

    def update(self, path):
        if self.session:
            self.session.close_all()
        self.session = init_sqlite_db(self.base, path=path)

    def get(self):
        if not self.session:
            raise Exception("Session not initialized")
        return self.session


class BaseExtended:
    def to_dict(self):
        columns = [c.name for c in self.__table__.columns]
        return {k: v for k, v in vars(self).items() if k in columns}
