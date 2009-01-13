import sys

from manager import Manager
import version_provider
import version_catalog

conn_str = 'sqlite:///dbtest.sqlite'

action = sys.argv[1].lower()

prov = version_provider.SqlVersionProvider(conn_str)
cat = version_catalog.FileSystemVersionsCatalog('versions')

m = Manager(provider=prov, catalog=cat)

if action == 'up':
    m.upgrade(sys.argv[2])
elif action == 'dn':
    m.downgrade(sys.argv[2])
elif action == 'del':
    m.uninstall()
else:
    print "Unknown action."
