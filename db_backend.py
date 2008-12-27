# -*- coding: utf-8 -*-

import sqlalchemy
import sqlalchemy.orm


class DbBackend(object):
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.engine = None
        self.connection = None

    def connect(self):
        self.engine = sqlalchemy.create_engine(self.connection_string, echo=True)
        self.connection = self.engine.connect()
        return self.connection

    def disconnect(self):
        self.connection.close()


class Session(object):
    """
    This class is used to avoid api breakages in sqlalchemy.
    """
    def __init__(self, connection):
        self.connection = connection
        Session = sqlalchemy.orm.sessionmaker(transactional=False)
        self.session = Session(bind=self.connection)
        self.transaction_began = False

    def execute(self, expression, *args, **kwargs):
        if not self.transaction_began:
            self.session.begin() # start transaction
        return self.session.execute(expression, *args, **kwargs)

    def commit(self):
        """
        Finishes transaction. You cannot re-use this session after attempting commit.
        """
        self.session.commit()
        self.connection.close()
        self.session = None
        self.connection = None
