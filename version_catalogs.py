# -*- coding: utf-8 -*-


class VersionsCatalogInterface(object):
    """
    Class that lists all available versions.
    """

    def get_available_versions(self):
        """ Returns list of available versions. """
        pass


class DummyVersionsCatalog(VersionsCatalogInterface):
    def __init__(self, versions_list):
        self.versions_list = versions_list

    def get_available_versions(self):
        return self.versions_list
