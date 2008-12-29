# -*- coding: utf-8 -*-

# Copyright (c) 2008 by Konstantin Merenkov <kmerenkov@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


import sqlalchemy
import sqlalchemy.orm


class BaseBackend(object):
    def __init__(self, _connection_string):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

class Backend(BaseBackend):
    def __init__(self, connection_string):
        super(Backend, self).__init__(connection_string)
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
        AlchemySession = sqlalchemy.orm.sessionmaker(transactional=False)
        self.session = AlchemySession(bind=self.connection)
        self.transaction_began = False

    def __cleanup(self):
        self.connection.close()
        self.connection = None
        self.session = None

    def execute(self, expression, *args, **kwargs):
        if not self.transaction_began:
            self.session.begin() # start transaction
            self.transaction_began = True
        return self.session.execute(expression, *args, **kwargs)

    def rollback(self):
        """
        Issue rollback on transaction. You cannot re-use this session after attempting rollback.
        """
        self.session.rollback()
        self.__cleanup()

    def commit(self):
        """
        Finishes transaction. You cannot re-use this session after attempting commit.
        """
        self.session.commit()
        self.__cleanup()
