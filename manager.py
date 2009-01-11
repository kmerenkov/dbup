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


class Manager(object):
    def __init__(self, connection_string=None, provider=None, catalog=None, backend=None):
        """
        You ask this class to upgrade/downgrade/etc your databases.
        provider. catalog, and backend are instnaces of derivatives of classes
        such as BaseVersionProvider, BaseVersionsCatalog, and BaseBackend.
        """
        self.connection_string = connection_string
        self.provider = provider
        self.catalog = catalog
        if backend is None:
            self.backend = database.backend.Backend(self.connection_string)
        else:
            self.backend = backend

    def calculate_range(self, frm, to, all_items):
        x = None
        y = None
        if frm in all_items:
            x = all_items.index(frm)
        if to in all_items:
            y = all_items.index(to)
        return (x, y)

    def build_patching_trace(self, to=None):
        cur_ver = self.provider.get_current_version()
        all_vers = self.catalog.get_available_versions()
        x, y = self.calculate_range(cur_ver, to, all_vers)
        trace = []
        if x is None: # fresh install, current version is unavailable
            if y is None: # if y is none, upgrade to the latest version available
                y = len(all_vers)
            trace = all_vers[:y+1]
            return (True, trace)
        elif x is not None: # it is upgrade or downgrade
            if y is None:
                y = len(all_vers) - 1
            if x < y: # upgrade
                trace = all_vers[x+1:y+1]
                return (True, trace)
            elif x > y: # downgrade
                trace = all_vers[y+1:x+1]
                trace.reverse()
                return (False, trace)
            else: # do nothing
                return (True, [])

    def process_stages(self, session, is_upgrading, stages):
        current_stage = None
        for stage_name in stages:
            current_stage = stage_name
            stage = self.catalog.load_stage(stage_name)
            if is_upgrading:
                stage.up(session)
            else:
                stage.down(session)
        # final touch, update current version value
        self.provider.set_current_version(current_stage)

    def uninstall(self):
        """
        You want to use this method to uninstall database.
        It will run downgrade on all stages, from current to first one installed.
        """
        cur_ver = self.provider.get_current_version()
        all_vers = self.catalog.get_available_versions()
        if cur_ver in all_vers:
            cur_ver_idx = all_vers.index(cur_ver)
        else:
            return
        trace = all_vers[:cur_ver_idx+1]
        trace.reverse()

        connection = self.backend.connect()
        session = database.backend.Session(connection)
        session.begin()
        self.process_stages(session, False, trace)
        self.provider.cleanup()
        session.commit()

    def change_version_to(self, new_version=None):
        """
        Will perform upgrading or downgrading, depends on currently installed version.
        """
        upgrading, trace = self.build_patching_trace(new_version)
        if not trace:
            return

        connection = self.backend.connect()
        session = database.backend.Session(connection)
        session.begin()
        self.process_stages(session, upgrading, trace)
        session.commit()
