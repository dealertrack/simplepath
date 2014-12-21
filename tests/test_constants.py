# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from simplepath.constants import FailMode


class TestConstants(unittest.TestCase):
    def test_is_valid_valid(self):
        self.assertTrue(FailMode.is_valid('default'))
        self.assertTrue(FailMode.is_valid('fail'))
        self.assertTrue(FailMode.is_valid('skip'))

    def test_is_valid_invalid(self):
        self.assertFalse(FailMode.is_valid('foo'))
