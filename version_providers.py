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


import db_backend


class VersionProviderInterface(object):
    """
    Class that implements version provider interface.
    Gives you an ability to look up current version of database
    and cchange it.
    """
    def get_current_version(self):
        """ Returns current version of database """
        pass

    def set_current_version(self, new_version):
        """ Updates current version value in database """
        pass


class VersionProvider(VersionProviderInterface):
    def __init__(self, connection_string, version_table='dbup_version'):
        super(VersionProvider, self).__init__()
        # NOTE example: 'sqlite:///relative/path/to/database.txt'
        self.connection_string = connection_string
        self.version_table = version_table

    def __get_session(self):
        backend = db_backend.DbBackend(self.connection_string)
        connection = backend.connect()
        session = db_backend.Session(connection)
        return session

    def get_current_version(self):
        session = self.__get_session()
        ret = session.execute("select * from %s;" % self.version_table)
        record = ret.fetchone()
        session.commit()
        return record[0]

    def set_current_version(self, new_version):
        session  =self.__get_session()
        session.execute("update %s set current_version=:new_version;" % self.version_table,
                        {'new_version': new_version})
        session.commit()
