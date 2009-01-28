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

import sys

from optparse import OptionParser

from manager import Manager
from worker import SqlWorker
import version_catalog


USAGE = """Usage: %prog ( up [ VER ] | down VER | delete | status )

    up [VER]    upgrade DB to version VER
                Ommit VER to upgrade to the latest available version.

    down VER    downgrade DB to version VER
                Downgrading to version 0 will leave you with that version, not before it.

    delete      downgrade before first version
                Will also destroy dbup internal information in DB.
                In clean case you expect no tables in database after this operation.

    status      show current version and exit"""

VALID_ACTIONS = ['up', 'down', 'delete', 'status']


def main(argv=sys.argv):
    parser = OptionParser(usage=USAGE)
    parser.add_option('-c', '--connection-string',
                      default="",
                      metavar="STRING",
                      help="Connection string to database server.")
    parser.add_option('-p', '--version-path',
                      default="",
                      metavar="PATH",
                      help="Path to versions.")

    options, arguments = parser.parse_args(argv)
    if len(arguments) < 2 or arguments[1] not in VALID_ACTIONS:
        parser.print_help()
        exit(1)

    if not all([options.connection_string, options.version_path]):
        parser.print_help()
        exit(1)

    worker = SqlWorker(options.connection_string)
    catalog = version_catalog.DirectoryVersionCatalog(options.version_path)
    manager = Manager(worker=worker, catalog=catalog)

    action = arguments[1]

    if action == 'up':
        ver = None
        if len(arguments) > 2:
            ver = arguments[2]
        manager.upgrade(ver)
    elif action == 'down':
        if len(arguments) > 2:
            ver = arguments[2]
        else:
            parser.print_help()
            exit(1)
        manager.downgrade(ver)
    elif action == 'delete':
        manager.uninstall()
    elif action == 'status':
        current_version = worker.get_current_version()
        if current_version is not None:
            print "Current version deployed: %s" % current_version
        else:
            print "No installation detected."


if __name__ == '__main__':
    main()
