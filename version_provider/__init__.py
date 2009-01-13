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


class SqlVersionProvider(object):
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
        # NOTE example: 'sqlite:///relative/path/to/database.txt'
        self.connection_string = connection_string
        self.version_table = version_table
        if backend is None:
            self.backend = database.backend.Backend(self.connection_string)
        else:
            self.backend = backend
        self.session = None

    def setup(self):
        self.__maybe_init_session()
        try:
            self.__create_table()
            self.session.commit()
        except:
            self.session.rollback()

    def upgrade(self, stages):
        self.setup()
        current_stage = None
        for stage_name, stage_instance in stages:
            current_stage = stage_name
            stage_instance.up(self.session)
        self.set_current_version(current_stage) # commit comes from this function
        self.session.close()

    def downgrade(self, stages):
        self.setup()
        downgrade_to = stages[-1][0]
        del stages[-1]
        for stage_name, stage_instance in stages:
            stage_instance.down(self.session)
        self.set_current_version(downgrade_to) # commit comes from this function
        self.session.close()

    def uninstall(self, stages):
        self.setup()
        for _stage_name, stage_instance in stages:
            stage_instance.down(self.session)
        self.cleanup()
        self.session.commit()
        self.session.close()

    def __maybe_init_session(self):
        if not self.session:
            connection = self.backend.connect()
            self.session = database.backend.Session(connection)

    def __create_table(self):
        self.session.execute("create table %s (current_version char(50));" % self.version_table)

    def get_current_version(self):
        """
        Returns current version installed, or None.
        None supposed to mean that there is no installation at all.
        """
        self.__maybe_init_session()
        try:
            ret = self.session.execute("select * from %s;" % self.version_table)
            record = ret.fetchone()
            self.session.commit()
        except Exception, _e:
            self.session.rollback()
            return None
        if record is not None:
            print "cur_ver: %s" % record[0]
            return record[0]
        else:
            print "cur_ver: %s" % None
            return None

    def set_current_version(self, new_version):
        """
        Updates current version record in database.
        Doesn't return anything.
        """
        self.__maybe_init_session()
        try:
            self.session.execute("delete from %s;" % self.version_table)
            self.session.execute("insert into %s values (:new_version);" % self.version_table,
                                 {'new_version': new_version})
            # self.session.execute("update %s set current_version=:new_version;" % self.version_table,
                            # {'new_version': new_version})
            self.session.commit()
            return
        except: # TBD: catch OperationalError from alchemy
            self.session.rollback()
        # if we've failed to update version, create the table and 'insert' new version
        # self.__create_table()
        # self.session.execute("insert into %s values (:new_version);" % self.version_table,
        #                 {'new_version': new_version})
        # self.session.commit()

    def cleanup(self):
        """
        Removes version information from database.
        """
        self.__maybe_init_session()
        try:
            self.session.execute("drop table %s;" % self.version_table)
            self.session.commit()
        except: # TBD: catch OperationalError from alchemy
            self.session.rollback()

