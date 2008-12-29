import sys

from manager import Manager
import version_provider
import version_catalog

conn_str = 'sqlite:///dbtest.sqlite'

ver_from = sys.argv[1]
ver_to = sys.argv[2]

if ver_from.lower() == 'none':
    ver_from = None
if ver_to.lower() == 'none':
    ver_to = None

prov = version_provider.SqlVersionProvider(conn_str)
cur_ver = prov.get_current_version()
print "Currently installed version: %s" % cur_ver
if cur_ver != ver_from:
    print "Changing currently installed version to: %s" % ver_from
    prov.set_current_version(ver_from)
    print "Double-checking, currently installed version: %s" % prov.get_current_version()

cat = version_catalog.FileSystemVersionsCatalog('versions')
print "Available versions: %s" % cat.get_available_versions()

m = Manager(connection_string=conn_str, provider=prov, catalog=cat)

print "Changing version to: %s" % ver_to
m.change_version_to(ver_to)
print "Uninstalling:"
m.uninstall()
