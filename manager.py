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

    def build_patching_trace(self, to=None):
        def is_upgrade(ver_from, ver_to):
            if not ver_to:
                return True
            x = [ver_from, ver_to]
            x.sort()
            if x[0] == ver_from:
                return True
            return False

        # get current version and all available versions
        cur_ver = self.provider.get_current_version()
        all_vers = self.catalog.get_available_versions()
        if cur_ver is None and all_vers:
            # we are installing, not upgrading or downgrading
            cur_ver = all_vers[0]
            if to and to not in all_vers:
                return None
            if not to:
                return (True, all_vers)
            else:
                to_ver_idx = all_vers.index(to) + 1
                return (True, all_vers[:to_ver_idx])
        if cur_ver not in all_vers:
            return None
        if to and to not in all_vers:
            return None
        cur_ver_idx = all_vers.index(cur_ver)
        # find out whether it's upgrade or downgrade
        upgrading = is_upgrade(cur_ver, to)
        if not upgrading:
            all_vers.reverse()
            to_ver_idx = all_vers.index(to)
        else:
            to_ver_idx = None
            if not to:
                to_ver_idx = len(all_vers)
            else:
                to_ver_idx = all_vers.index(to) + 1
        trace = all_vers[cur_ver_idx+1:to_ver_idx]
        return (upgrading, trace)

    def change_version_to(self, new_version=None):
        upgrading, trace = self.build_patching_trace(new_version)
        if not trace:
            return
        connection = self.backend.connect()
        session = database.backend.Session(connection)
        current_stage = None
        for stage_name in trace:
            current_stage = stage_name
            stage = self.catalog.load_stage(stage_name)
            if upgrading:
                stage.up(session)
            else:
                stage.down(session)
        # final touch, update current version value
        self.provider.set_current_version(current_stage)
        session.commit()
