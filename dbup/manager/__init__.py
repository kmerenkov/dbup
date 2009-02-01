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


from dbup.worker import NoInstallation


class NothingToDo(Exception):
    class ACTION(object):
        upgrade = 0
        downgrade = 1


    def __init__(self, current_version=None, to_version=None, action=None):
        self.current_version = current_version
        self.to_version = to_version
        self.action = action


class UnavailableVersion(Exception):
    def __init__(self, version=None, all_versions=None):
        self.version = version
        self.all_versions = all_versions


class Manager(object):
    def __init__(self, worker=None, catalog=None):
        """
        You ask this class to upgrade/downgrade/etc your databases.
        """
        self.worker = worker
        self.catalog = catalog

    def upgrade(self, to_version):
        try:
            current_version = self.worker.get_current_version()
        except NoInstallation:
            current_version = None
        available_versions = self.catalog.get_available_versions()

        # if destination version is not specified, use latest available
        if to_version is None:
            to_version = available_versions[-1]

        # check if we need upgrade at all
        if current_version == to_version:
            raise NothingToDo(current_version=current_version,
                              to_version=to_version,
                              action=NothingToDo.ACTION.upgrade)
        if current_version is not None:
            if available_versions.index(to_version) < available_versions.index(current_version):
                raise NothingToDo(current_version=current_version,
                                  to_version=to_version,
                                  action=NothingToDo.ACTION.upgrade)

        # ok, upgrading
        stages = []
        if current_version in available_versions:
            current_version_idx = available_versions.index(current_version)
        else:
            current_version_idx = -1
        # check whether requested version is available or not
        if to_version not in available_versions:
            raise UnavailableVersion(version=to_version,
                                     all_versions=available_versions)
        to_version_idx = available_versions.index(to_version)
        needed_versions = available_versions[current_version_idx+1: to_version_idx+1]
        # build list of stages, where every list item is (version name, initialized stage object)
        stages = [ (version, self.catalog.load_stage(version)) for version in needed_versions ]
        self.worker.upgrade(stages)

    def downgrade(self, to_version):
        current_version = self.worker.get_current_version() # NOTE throws NoInstallation exception
        available_versions = self.catalog.get_available_versions()
        # check if we need downgrade at all
        if current_version == to_version:
            raise NothingToDo(current_version=current_version,
                              to_version=to_version,
                              action=NothingToDo.ACTION.downgrade)
        if current_version is not None:
            if available_versions.index(to_version) > available_versions.index(current_version):
                raise NothingToDo(current_version=current_version,
                                  to_version=to_version,
                                  action=NothingToDo.ACTION.downgrade)
        # check whether installed version is available or not
        if current_version not in available_versions:
            raise UnavailableVersion(version=current_version,
                                     all_versions=available_versions)
        else:
            current_version_idx = available_versions.index(current_version)
        # check whether requested version is available or not
        if to_version not in available_versions:
            raise UnavailableVersion(version=to_version,
                                     all_versions=available_versions)

        # ok, downgrading
        to_version_idx = available_versions.index(to_version)
        needed_versions = available_versions[ to_version_idx: current_version_idx+1 ]
        # build list of stages, where every list item is (version name, initialized stage object)
        needed_versions.reverse()
        stages = [ (version, self.catalog.load_stage(version)) for version in needed_versions ]
        self.worker.downgrade(stages)

    def uninstall(self):
        current_version = self.worker.get_current_version() # NOTE throws NoInstallation exception
        available_versions = self.catalog.get_available_versions()
        stages = []
        if current_version in available_versions:
            current_version_idx = available_versions.index(current_version)
        else:
            raise UnavailableVersion(version=current_version,
                                     all_versions=available_versions)
        needed_versions = available_versions[:current_version_idx+1]
        needed_versions.reverse()
        stages = [ (version, self.catalog.load_stage(version)) for version in needed_versions ]
        self.worker.uninstall(stages)

