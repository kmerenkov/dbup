#!/usr/bin/env python

# Copyright (c) 2009 by Konstantin Merenkov <kmerenkov@gmail.com>
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


from distutils.core import setup
import re


def get_version():
    return '1.0'

def get_author():
    return 'Konstantin Merenkov <kmerenkov@gmail.com>'

def get_author_email():
    author = get_author()
    re_email = re.compile(r'.*\<(?P<email>.+)\>.*')
    m = re_email.match(author)
    if m:
        return m.group('email')
    else:
        return None


setup(name='dbup',
      version=get_version(),
      description='blah blah',
      author=get_author(),
      author_email=get_author_email(),
      maintainer=get_author(),
      maintainer_email=get_author_email(),
      license='MIT',
      url='http://github.com/kmerenkov/dbup/tree/master',
      packages=['dbup',
                'dbup/version_catalog',
                'dbup/worker',
                'dbup/database'],
      )
