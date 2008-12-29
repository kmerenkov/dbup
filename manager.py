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
        if frm not in all_items or to not in all_items:
            return (None, None)
        frm_idx = all_items.index(frm)
        to_idx = all_items.index(to)
        return (frm_idx, to_idx)

    def build_patching_trace(self, to=None):
        cur_ver = self.provider.get_current_version()
        all_vers = self.catalog.get_available_versions()
        if not all_vers:
            return None
        if to is None:
            to = all_vers[-1]
        if cur_ver is None: # fresh install
            cur_ver = all_vers[0]
        x, y = self.calculate_range(cur_ver, to, all_vers)
        if x == y == None:
            return None
        if x > y:
            retval = all_vers[y:x]
            retval.reverse()
            return (False, retval)
        else:
            return (True, all_vers[x:y+1])


    def process_stages(self, is_upgrading, stages):
        connection = self.backend.connect()
        session = database.backend.Session(connection)
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
        session.commit()

    def uninstall(self):
        _upgrading, trace = self.build_patching_trace(None, downgrade_inclusive=True)
        if not trace:
            return
        self.process_stages(False, trace)

    def change_version_to(self, new_version=None):
        upgrading, trace = self.build_patching_trace(new_version)
        if not trace:
            return
        self.process_stages(upgrading, trace[1:])
