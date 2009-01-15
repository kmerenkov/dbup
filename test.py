#!/usr/bin/env python

import sys

from optparse import OptionParser

from dbup.manager import Manager
from dbup.worker import SqlWorker
from dbup import version_catalog


USAGE = """Usage: %prog ( up [ VER ] | down VER | delete | check )

    up [VER]    upgrade DB to version VER
                Ommit VER to upgrade to the latest available version.

    down VER    downgrade DB to version VER
                Downgrading to version 0 will leave you with that version, not before it.

    delete      downgrade before first version
                Will also destroy dbup internal information in DB.
                In clean case you expect no tables in database after this operation.

    check       show current version and exit"""

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
