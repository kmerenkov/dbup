import version_providers
import version_catalogs


class Manager(object):
    def __init__(self, provider=None, catalog=None):
        self.provider = provider
        self.catalog = catalog

    def build_patching_trace(self, to=None):
        def is_upgrade(ver_from, ver_to):
            if not ver_to:
                return True
            x = [ver_from, ver_to]
            x.sort()
            if x[0] == ver_from:
                return True
            return False

        # get current version and all available versions
        cur_ver = self.provider.get_current_version()
        all_vers = self.catalog.get_available_versions()
        all_vers.sort()
        if cur_ver not in all_vers:
            return None
        if to and to not in all_vers:
            return None
        # find out whether it's upgrade or downgrade
        if not is_upgrade(cur_ver, to):
            all_vers.reverse()
        cur_ver_idx = all_vers.index(cur_ver)
        to_ver_idx = None
        if not to: # cannot happen with downgrade
            to_ver_idx = len(all_vers)
        else:
            to_ver_idx = all_vers.index(to) + 1
        return all_vers[cur_ver_idx+1:to_ver_idx]
