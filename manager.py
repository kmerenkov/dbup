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
# from sqlalchemy.exceptions import OperationalError


class Manager(object):
    def __init__(self, provider=None, catalog=None):
        """
        You ask this class to upgrade/downgrade/etc your databases.
        """
        self.provider = provider
        self.catalog = catalog

    def upgrade(self, to_version):
        current_version = self.provider.get_current_version()
        available_versions = self.catalog.get_available_versions()
        stages = []
        if current_version in available_versions:
            current_version_idx = available_versions.index(current_version)
        else:
            current_version_idx = -1
        if to_version in available_versions:
            to_version_idx = available_versions.index(to_version)
        else:
            print "to_version not in list of available versions (%s)" % available_versions
            return None
        needed_versions = available_versions[current_version_idx+1: to_version_idx+1]
        for version in needed_versions:
            stage = self.catalog.load_stage(version)
            stages.append((version, stage,))
        self.provider.upgrade(stages)

    def downgrade(self, to_version):
        current_version = self.provider.get_current_version()
        available_versions = self.catalog.get_available_versions()
        stages = []
        if current_version in available_versions:
            current_version_idx = available_versions.index(current_version)
        else:
            print "no installation detected"
            return None
        if to_version in available_versions:
            to_version_idx = available_versions.index(to_version)
        else:
            print "to_version not in list of available versions (%s)" % available_versions
            return None
        needed_versions = available_versions[to_version_idx: current_version_idx+1]
        needed_versions.reverse()
        for version in needed_versions:
            stage = self.catalog.load_stage(version)
            stages.append((version, stage,))
        self.provider.downgrade(stages)

    def uninstall(self):
        current_version = self.provider.get_current_version()
        available_versions = self.catalog.get_available_versions()
        stages = []
        if current_version in available_versions:
            current_version_idx = available_versions.index(current_version)
        else:
            print "no installation detected"
            return None
        needed_versions = available_versions[:current_version_idx+1]
        needed_versions.reverse()
        for version in needed_versions:
            stage = self.catalog.load_stage(version)
            stages.append((version, stage,))
        self.provider.uninstall(stages)
