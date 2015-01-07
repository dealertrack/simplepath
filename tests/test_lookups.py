# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

import mock

from simplepath.lookups import (
    BaseLookup,
    FindInListLookup,
    KeyLookup,
    LUTLookup,
)


class TestBaseLookup(unittest.TestCase):
    def setUp(self):
        super(TestBaseLookup, self).setUp()
        self.lookup = BaseLookup()

    def test_config(self):
        self.assertIsNone(self.lookup.config())

    @mock.patch.object(BaseLookup, 'config')
    def test_setup(self, mock_config):
        # sanity checks
        self.assertFalse(hasattr(self, 'expression'))

        actual = self.lookup.setup(expression='{hello}')

        self.assertEqual(self.lookup.expression, '{hello}')
        self.assertIs(actual, self.lookup)
        mock_config.assert_called_once_with()

    def test_repr(self):
        self.assertEqual(self.lookup.repr(), '')

    def test_call_expression(self):
        expression = mock.MagicMock()

        actual = self.lookup.call_expression(
            expression,
            mock.sentinel.data,
            {
                'super_root': mock.sentinel.super_root,
                'lut': mock.sentinel.lut,
                'context': mock.sentinel.context,
            }
        )

        self.assertEqual(actual, expression.return_value)
        expression.assert_called_once_with(
            mock.sentinel.data,
            super_root=mock.sentinel.super_root,
            lut=mock.sentinel.lut,
            context=mock.sentinel.context,
        )

    def test_call(self):
        with self.assertRaises(NotImplementedError):
            self.lookup(node=None)

    def test__repr(self):
        self.assertEqual(repr(self.lookup), '<BaseLookup >')


class TestKeyLookup(unittest.TestCase):
    def setUp(self):
        super(TestKeyLookup, self).setUp()
        self.lookup = KeyLookup()

    def test_config(self):
        self.lookup.config('foo')

        self.assertEqual(self.lookup.key, 'foo')

    def test_call_list(self):
        self.lookup.key = '0'

        actual = self.lookup(['foo'])

        self.assertEqual(actual, 'foo')

    def test_call_dict(self):
        self.lookup.key = 'foo'

        actual = self.lookup({'foo': 'bar'})

        self.assertEqual(actual, 'bar')

    def test_repr(self):
        self.lookup.key = 'foo'

        self.assertEqual(self.lookup.repr(), 'key="foo"')


class TestFindInListLookup(unittest.TestCase):
    def setUp(self):
        super(TestFindInListLookup, self).setUp()
        self.lookup = FindInListLookup()

    def test_config(self):
        self.lookup.config(foo='bar')

        self.assertDictEqual(
            self.lookup.conditions,
            {'foo': 'bar'}
        )

    def test_call_exists(self):
        self.lookup.conditions = {'foo': 'bar'}
        data = [
            {
                'happy': 'rainbows',
            },
            {
                'foo': 'bar',
                'happy': 'rainbows',
            },
            {
                'foo': 'foo',
                'happy': 'rainbows',
            },
        ]

        actual = self.lookup(data)

        self.assertDictEqual(actual, data[1])

    def test_call_does_not_exist(self):
        self.lookup.conditions = {'foo': 'barbar'}
        data = [
            {
                'happy': 'rainbows',
            },
            {
                'foo': 'bar',
                'happy': 'rainbows',
            },
            {
                'foo': 'foo',
                'happy': 'rainbows',
            },
        ]

        with self.assertRaises(ValueError):
            self.lookup(data)

    def test_repr(self):
        self.lookup.conditions = {
            'foo': 'bar',
        }

        self.assertEqual(self.lookup.repr(), 'foo="bar"')


class TestLUTLookup(unittest.TestCase):
    def setUp(self):
        super(TestLUTLookup, self).setUp()
        self.lookup = LUTLookup()

    def test_call(self):
        self.lookup.key = 'foo'

        actual = self.lookup(None, extra={'lut': {'foo': 'bar'}})

        self.assertEqual(actual, 'bar')
