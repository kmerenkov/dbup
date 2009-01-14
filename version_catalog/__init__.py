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


class PlainFilesVersionCatalog(object):
    """
    Version catalog that finds patches that live in one directory as simple python scripts.
    Example:
      ./dir/
          + 01.py
          + 02.py
          + 03.py
          ...
    """
    def __init__(self, path='.'):
        self.path = path

    def get_available_versions(self):
        versions = [ f[:-3] for f in os.listdir(self.path) if not os.path.isdir(f) and f.endswith('.py') ]
        versions.sort()
        return versions

    def load_stage(self, version):
        stage_module = __import__(os.path.join(self.path, version))
        Stage = getattr(stage_module, "Stage", None)
        return Stage()


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
        versions = [ d for d in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, d)) ]
        versions.sort()
        return versions

    def load_stage(self, version):
        stage_module = __import__(os.path.join(self.path, version))
        Stage = getattr(stage_module, "Stage", None)
        return Stage()
