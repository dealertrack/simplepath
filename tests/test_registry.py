# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from simplepath.registry import LookupRegistry


class TestLookupRegistry(unittest.TestCase):
    def setUp(self):
        super(TestLookupRegistry, self).setUp()
        self.registry = LookupRegistry('foo')

    def test_name(self):
        self.assertEqual(self.registry.name, 'foo')

    def test_register(self):
        self.assertNotIn('foo', self.registry)

        self.registry.register('foo', 'bar')

        self.assertEqual(self.registry['foo'], 'bar')
