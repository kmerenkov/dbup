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
import sys


j = os.path.join


class DirectoryVersionCatalog(object):
    """
    Version catalog that finds patches that live in one directory as directories with __init__.py inside.
    Useful if you ship fixtures along with the patches.
    Example:
      ./dir/
          + 01/__init__.py
          + 01/some_fixture
          + 02/__init__.py
          + 03/__init__.py
          ...
    """
    def __init__(self, path='.'):
        self.path = path

    def get_available_versions(self):
        versions = [ d for d in os.listdir(self.path) if os.path.isdir(j(self.path, d)) ]
        versions.sort()
        return versions

    def load_stage(self, version):
        # At this point, <version>/__init__.py must be import-able
        stage_module = {}
        version_path = j(self.path, version, '__init__.py')
        if not os.path.isfile(version_path):
            raise Exception("Could not find version file %s" % (version_path))
        execfile(version_path, stage_module)
        Stage = stage_module['Stage']
        stage = Stage()
        stage.current_path = os.path.abspath(j(self.path, version))
        return stage
