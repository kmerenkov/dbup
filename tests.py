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


class DummyVersionProvider(version_provider.BaseVersionProvider):
    def __init__(self, version_to_return):
        super(DummyVersionProvider, self).__init__()
        self.version_to_return = version_to_return

    def get_current_version(self):
        return self.version_to_return

    def set_current_version(self, new_version):
        self.version_to_return = new_version


class DummyVersionsCatalog(version_catalog.BaseVersionsCatalog):
    def __init__(self, versions_list):
        super(DummyVersionsCatalog, self).__init__()
        self.versions_list = versions_list

    def get_available_versions(self):
        return self.versions_list


class ManagerTestCase(unittest.TestCase):
    def test_build_patching_trace_001(self):
        dummy_provider = DummyVersionProvider('3.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('3.0')
        expected = (True, ['3.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_002(self):
        dummy_provider = DummyVersionProvider('1.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('5.0')
        expected = (True, ['1.0', '2.0', '3.0', '4.0', '5.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_003(self):
        dummy_provider = DummyVersionProvider('3.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('1.0')
        expected = (False, ['2.0', '1.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_004(self):
        dummy_provider = DummyVersionProvider('1.0')
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace()
        expected = (True, ['1.0', '2.0', '3.0', '4.0', '5.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_005(self):
        dummy_provider = DummyVersionProvider(None)
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace()
        expected = (True, ['1.0', '2.0', '3.0', '4.0', '5.0'])
        self.assertEqual(actual, expected)

    def test_build_patching_trace_006(self):
        dummy_provider = DummyVersionProvider(None)
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=dummy_provider, catalog=dummy_catalog)
        actual = m.build_patching_trace('3.0')
        expected = (True, ['1.0', '2.0', '3.0'])
        self.assertEqual(actual, expected)

    def test_calculate_range_001(self):
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=None, catalog=dummy_catalog)
        actual = m.calculate_range('1.0', '5.0', dummy_catalog.get_available_versions())
        expected = (0, 4)
        self.assertEqual(actual, expected)

    def test_calculate_range_002(self):
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=None, catalog=dummy_catalog)
        actual = m.calculate_range('5.0', '1.0', dummy_catalog.get_available_versions())
        expected = (4, 0)
        self.assertEqual(actual, expected)

    def test_calculate_range_003(self):
        dummy_catalog = DummyVersionsCatalog(['1.0', '2.0', '3.0', '4.0', '5.0'])
        m = manager.Manager(provider=None, catalog=dummy_catalog)
        actual = m.calculate_range('1.0', '4.0', dummy_catalog.get_available_versions())
        expected = (0, 3)
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
