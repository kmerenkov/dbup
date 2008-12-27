#!/usr/bin/env python

import unittest

import version_providers
import version_catalogs
import manager


class DummyVersionProvider(version_providers.VersionProviderInterface):
    def __init__(self, version_to_return):
        self.version_to_return = version_to_return

    def get_current_version(self):
        return self.version_to_return

    def set_current_version(self, new_version):
        self.version_to_return = new_version


class DummyVersionsCatalog(version_catalogs.VersionsCatalogInterface):
    def __init__(self, versions_list):
        self.versions_list = versions_list

    def get_available_versions(self):
        return self.versions_list



class ManagerTestCase(unittest.TestCase):
    def test_build_patching_trace_001(self):
        """ Must not advice any upgrades/downgrades when trying to deploy already deployed version. """
        dummy_provider = DummyVersionProvider('3.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('3.0')
        expected = []
        self.assertEqual(actual, expected)

    def test_build_patching_trace_002(self):
        """ Must advice upgrade from 1.0 to 5.0 """
        dummy_provider = DummyVersionProvider('1.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('5.0')
        expected = ['2.0', '3.0', '4.0', '5.0']
        self.assertEqual(actual, expected)

    def test_build_patching_trace_003(self):
        """ Must advice downgrade from 3.0 to 1.0 """
        dummy_provider = DummyVersionProvider('3.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('1.0')
        expected = ['2.0', '1.0']
        self.assertEqual(actual, expected)

    def test_build_patching_trace_004(self):
        """ When destination version isn't specified, treat it as last version possiblee """
        dummy_provider = DummyVersionProvider('1.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace()
        expected = ['2.0', '3.0', '4.0', '5.0']
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
