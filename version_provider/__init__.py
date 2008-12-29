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


import database.backend


class BaseVersionProvider(object):
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


class SqlVersionProvider(BaseVersionProvider):
    """
    Class that implements sql-interface to get/set current version.
    If you want to implement more advanced logic for get_current_version
    and set_current_version, you just have to inherit this class and
    re-implement these methods.
    """
    def __init__(self, connection_string, version_table='dbup_version', backend=None):
        """
        version_table - table where current version number is kept.
        """
        super(BaseVersionProvider, self).__init__()
        # NOTE example: 'sqlite:///relative/path/to/database.txt'
        self.connection_string = connection_string
        self.version_table = version_table
        if backend is None:
            self.backend = database.backend.Backend(self.connection_string)
        else:
            self.backend = backend

    def get_session(self):
        """
        For internal use only. Connects to database and returns a session.
        You want to call for this function if you are overriding
        set_current_version and get_current_version.
        """
        connection = self.backend.connect()
        session = self.backend.Session(connection)
        return session

    def __create_table(self):
        session = self.get_session()
        session.execute("create table %s (current_version char(50));" % self.version_table)
        session.commit()

    def get_current_version(self):
        """
        Returns current version installed, or None.
        None supposed to mean that there is no installation at all.
        """
        session = self.get_session()
        try:
            ret = session.execute("select * from %s;" % self.version_table)
            record = ret.fetchone()
            session.commit()
        except:
            session.rollback()
            return None
        return record[0]

    def set_current_version(self, new_version):
        """
        Updates current version record in database.
        Doesn't return anything.
        """
        session = self.get_session()
        try:
            session.execute("update %s set current_version=:new_version;" % self.version_table,
                            {'new_version': new_version})
            session.commit()
            return
        except: # TBD: catch OperationalError from alchemy
            session.rollback()
        # if we've failed to update version, create the table and 'insert' new version
        self.__create_table()
        session = self.get_session()
        session.execute("insert into %s values (:new_version);" % self.version_table,
                        {'new_version': new_version})
        session.commit()
