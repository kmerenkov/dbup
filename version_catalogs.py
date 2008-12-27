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


import os


class VersionsCatalogInterface(object):
    """
    Class that lists all available versions.
    """

    def get_available_versions(self):
        """ Returns list of available versions. """
        pass

    def load_stage(self, version):
        pass


class FileSystemVersionsCatalog(VersionsCatalogInterface):
    def __init__(self, path='.'):
        self.path = path

    def get_available_versions(self):
        versions = [ f[:-3] for f in os.listdir(self.path) if not os.path.isdir(f) and f.endswith('.py') ]
        versions.sort()
        return versions

    def load_stage(self, version):
        stage_module = __import__(self.path + '/' + version) # TBD dirtiness, make it look better
        Stage = getattr(stage_module, "Stage", None)
        return Stage()
