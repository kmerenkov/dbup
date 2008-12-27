# -*- coding: utf-8 -*-

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
