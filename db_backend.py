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
