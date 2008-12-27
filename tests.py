#!/usr/bin/env python

# Copyright (c) 2008 by Konstantin Merenkov <kmerenkov@gmail.com>
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


import unittest

import version_provider
import version_catalog
import manager


class DummyVersionProvider(version_provider.VersionProviderInterface):
    def __init__(self, version_to_return):
        self.version_to_return = version_to_return

    def get_current_version(self):
        return self.version_to_return

    def set_current_version(self, new_version):
        self.version_to_return = new_version


class DummyVersionsCatalog(version_catalog.VersionsCatalogInterface):
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
        expected = (True, [])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_002(self):
        """ Must advice upgrade from 1.0 to 5.0 """
        dummy_provider = DummyVersionProvider('1.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('5.0')
        expected = (True, ['2.0', '3.0', '4.0', '5.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_003(self):
        """ Must advice downgrade from 3.0 to 1.0 """
        dummy_provider = DummyVersionProvider('3.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('1.0')
        expected = (False, ['2.0', '1.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_004(self):
        """ When destination version isn't specified, treat it as last version possiblee """
        dummy_provider = DummyVersionProvider('1.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace()
        expected = (True, ['2.0', '3.0', '4.0', '5.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_005(self):
        """ If current version is None, include all versions into trace """
        dummy_provider = DummyVersionProvider(None)
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace()
        expected = (True, ['1.0', '2.0', '3.0', '4.0', '5.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_006(self):
        """ If current version is None, include all versions prior to specified """
        dummy_provider = DummyVersionProvider(None)
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('3.0')
        expected = (True, ['1.0', '2.0', '3.0'])
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
