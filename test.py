import sys

from manager import Manager
import worker
import version_catalog

conn_str = 'sqlite:///dbtest.sqlite'

action = sys.argv[1].lower()

prov = worker.SqlWorker(conn_str)
cat = version_catalog.FileSystemVersionsCatalog('example_versions')

m = Manager(provider=prov, catalog=cat)

if action == 'up':
    m.upgrade(sys.argv[2])
elif action == 'dn':
    m.downgrade(sys.argv[2])
elif action == 'del':
    m.uninstall()
elif action == 'cur':
    cur_ver = prov.get_current_version()
    if cur_ver is not None:
        print "Current version deployed: %s" % cur_ver
    else:
        print "No installation detected."
else:
    print "Unknown action."
