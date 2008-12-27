import version_providers
import version_catalogs


class Manager(object):
    def __init__(self):
        self.provider = version_providers.DummyVersionProvider('1.0')
        self.catalog = version_catalogs.DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])

    def build_patching_trace(self, to=None):
        cur_ver = self.provider.get_current_version()
        all_vers = self.catalog.get_available_versions()
        all_vers.sort()
        if cur_ver not in all_vers:
            return None
        if to and to not in all_vers:
            return None
        cur_ver_idx = all_vers.index(cur_ver)
        to_ver_idx = None
        if not to:
            to_ver_idx = len(all_vers)
        else:
            to_ver_idx = all_vers.index(to)
        return all_vers[cur_ver_idx+1:to_ver_idx]
