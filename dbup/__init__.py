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

from manager import Manager, NothingToDo, UnavailableVersion
from worker import SqlWorker, NoInstallation
from database.backend import Backend
import version_catalog


USAGE = """Usage: %prog ( up [ VER ] | down VER | delete | status )

    up [VER]    upgrade DB to version VER
                Ommit VER to upgrade to the latest available version.

    down VER    downgrade DB to version VER
                Downgrading to version 0 will leave you with that version, not before it.

    delete      downgrade before first version
                Will also destroy dbup internal information in DB.
                In clean case you expect no tables in database after this operation.

    status      show current version and exit."""

VALID_ACTIONS = ['up', 'down', 'delete', 'status']


def create_instance(cls_info):
    """
    Creates instance of a class specified in cls_info.
    cls_info's format is (class_name, args, kwargs)
    e.g.:
       create_instance((dict, None, None))
    """
    cls, args, kwargs = cls_info
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    return cls(*args, **kwargs)

def main(argv=sys.argv,
         override_manager=None,
         override_catalog=None,
         override_worker=None):
    """
    argv - command line arguments, defaults to sys.argv
    override manager, catalog, worker - None or (class, args, kwargs)
    """
    parser = OptionParser(usage=USAGE)
    parser.add_option('-c', '--connection-string',
                      default="",
                      metavar="STRING",
                      help="Connection string to database server (scheme://user:pwd@host/database).")
    parser.add_option('-p', '--version-path',
                      default="",
                      metavar="PATH",
                      help="Path to versions.")
    parser.add_option('-v', '--verbose',
                      default=False,
                      action="store_true",
                      help="Print debug messages")

    options, arguments = parser.parse_args(argv)
    if len(arguments) < 2 or arguments[1] not in VALID_ACTIONS:
        parser.print_help()
        exit(1)

    if not all([options.connection_string, options.version_path]):
        parser.print_help()
        exit(1)

    # Create instances of worker, catalog, and manager.
    # They are possibly overriden from outside.
    if override_worker:
        worker = create_instance(override_worker)
    else:
        backend = Backend(options.connection_string, echo=options.verbose)
        worker = SqlWorker(backend=backend)
    if override_catalog:
        catalog = create_instance(override_catalog)
    else:
        catalog = version_catalog.DirectoryVersionCatalog(options.version_path)
    if override_manager:
        manager = create_instance(override_manager)
    else:
        manager = Manager(worker=worker, catalog=catalog)

    # setup worker events
    worker.onNewTask += lambda version: sys.stdout.write("[%s] " % version)
    worker.onTaskCompleted += lambda _version: sys.stdout.write("OK\n")
    worker.onVersionChanged += lambda version: sys.stdout.write("New version: \"%s\".\n" % version)
    worker.onFailedToChangeVersion += lambda version: sys.stdout.write("Failed to set version to \"%s\".\n" % version)
    worker.onCleanedUp += lambda: sys.stdout.write("Removed version information from database.\n")
    worker.onFailedToCleanUp  += lambda: sys.stdout.write("Failed to remove version information from database.\n")

    action = arguments[1]

    if action == 'up':
        ver = None
        if len(arguments) > 2:
            ver = arguments[2]
        try:
            worker.onNewTaskGroup += lambda: sys.stdout.write("Upgrading...\n")
            worker.onTaskGroupCompleted += lambda: sys.stdout.write("Upgrading has been completed.\n")
            manager.upgrade(ver)
        except NothingToDo, e:
            if e.current_version == e.to_version:
                print "Already up to date (version \"%s\")." % e.current_version
                exit(0)
            else:
                print "Cannot upgrade from \"%s\" to \"%s\"." % (e.current_version,
                                                                 e.to_version)
                exit(1)
        except UnavailableVersion, e:
            print "Requested version \"%s\" is not available.\n" % e.version + \
                  "Available versions: %s" % ", ".join(e.all_versions)
            exit(1)
    elif action == 'down':
        if len(arguments) > 2:
            ver = arguments[2]
        else:
            parser.print_help()
            exit(1)
        try:
            worker.onNewTaskGroup += lambda: sys.stdout.write("Downgrading...\n")
            worker.onTaskGroupCompleted += lambda: sys.stdout.write("Downgrading has been completed.\n")
            manager.downgrade(ver)
        except NoInstallation:
            print "No installation detected."
            exit(1)
        except NothingToDo, e:
            if e.current_version == e.to_version:
                print "Already up to date (version \"%s\")." % e.current_version
                exit(0)
            else:
                print "Cannot downgrade from \"%s\" to \"%s\"." % (e.current_version,
                                                                   e.to_version)
                exit(1)
        except UnavailableVersion, e:
            if e.version == ver: # to_version is not available
                print "Requested version \"%s\" is not available.\n" % e.version + \
                      "Available versions: %s" % ", ".join(e.all_versions)
            else:
                print "Currently installed version \"%s\" is not available.\n" % e.version + \
                      "Available versions: %s.\n" % ", ".join(e.all_versions) + \
                      "Cannot downgrade."
            exit(1)
    elif action == 'delete':
        try:
            worker.onNewTaskGroup += lambda: sys.stdout.write("Uninstalling...\n")
            worker.onTaskGroupCompleted += lambda: sys.stdout.write("Unintallation has been completed.\n")
            manager.uninstall()
        except NoInstallation:
            print "No installation detected."
            exit(1)
        except UnavailableVersion, e:
            print "Currently installed version \"%s\" is not available.\n" % e.version + \
                  "Available versions: %s.\n" % ", ".join(e.all_versions) + \
                  "Cannot downgrade."
            exit(1)
    elif action == 'status':
        try:
            current_version = worker.get_current_version()
            print "Current version installed: %s" % current_version
        except NoInstallation:
            print "No installation detected."
            exit(0)


if __name__ == '__main__':
    main()
