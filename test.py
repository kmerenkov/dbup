#!/usr/bin/env python

import sys

from manager import Manager
import worker
import version_catalog

conn_str = 'sqlite:///dbtest.sqlite'

action = sys.argv[1].lower()

worker = worker.SqlWorker(conn_str)
catalog = version_catalog.PlainFilesVersionCatalog('example_catalogs/plain_files')
# catalog = version_catalog.DirectoryVersionCatalog('example_catalogs/directories')

m = Manager(worker=worker, catalog=catalog)

if action == 'up':
    if len(sys.argv) <3:
        m.upgrade(None)
    else:
        m.upgrade(sys.argv[2])
elif action == 'dn':
    m.downgrade(sys.argv[2])
elif action == 'del':
    m.uninstall()
elif action == 'cur':
    cur_ver = worker.get_current_version()
    if cur_ver is not None:
        print "Current version deployed: %s" % cur_ver
    else:
        print "No installation detected."
else:
    print "Unknown action."
