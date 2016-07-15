# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import operator
import unittest
from decimal import Decimal

import mock

from simplepath.constants import FailMode
from simplepath.expressions import Expression
from simplepath.lookups import (
    ArithmeticLookup,
    AsTypeLookup,
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
            lut={},
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


class TestAsTypeLookup(unittest.TestCase):
    def setUp(self):
        super(TestAsTypeLookup, self).setUp()
        self.astype_lookup = AsTypeLookup()

    def test_config_int(self):
        self.astype_lookup.config('int')
        self.assertEqual(self.astype_lookup.type, int)

    def test_config_float(self):
        self.astype_lookup.config('float')
        self.assertEqual(self.astype_lookup.type, float)

    def test_config_decimal(self):
        self.astype_lookup.config('decimal')
        self.assertEqual(self.astype_lookup.type, Decimal)

    def test_config_bool(self):
        self.astype_lookup.config('bool')
        self.assertEqual(self.astype_lookup.type, bool)

    def test_config_invalid_type(self):
        self.assertRaises(ValueError, self.astype_lookup.config, 'invalid')

    def test_call(self):
        self.astype_lookup.type = Decimal
        self.assertEqual(Decimal('15.01'), self.astype_lookup('15.01'))


class TestArithmeticLookup(unittest.TestCase):
    def setUp(self):
        super(TestArithmeticLookup, self).setUp()
        self.arith_lookup = ArithmeticLookup()

    def test_config_truediv(self):
        self.arith_lookup.config('/', '15')
        self.assertEqual(self.arith_lookup.operator, operator.truediv)
        self.assertEqual(self.arith_lookup.operand, '15')
        self.assertEqual(self.arith_lookup.reverse, False)

    def test_config_floordiv(self):
        self.arith_lookup.config('//', '15')
        self.assertEqual(self.arith_lookup.operator, operator.floordiv)
        self.assertEqual(self.arith_lookup.operand, '15')
        self.assertEqual(self.arith_lookup.reverse, False)

    def test_config_add(self):
        self.arith_lookup.config('+', '15')
        self.assertEqual(self.arith_lookup.operator, operator.add)
        self.assertEqual(self.arith_lookup.operand, '15')
        self.assertEqual(self.arith_lookup.reverse, False)

    def test_config_sub(self):
        self.arith_lookup.config('-', '15', True)
        self.assertEqual(self.arith_lookup.operator, operator.sub)
        self.assertEqual(self.arith_lookup.operand, '15')
        self.assertEqual(self.arith_lookup.reverse, True)

    def test_config_mul(self):
        self.arith_lookup.config('*', '15')
        self.assertEqual(self.arith_lookup.operator, operator.mul)
        self.assertEqual(self.arith_lookup.operand, '15')
        self.assertEqual(self.arith_lookup.reverse, False)

    def test_config_pow(self):
        self.arith_lookup.config('^', '15')
        self.assertEqual(self.arith_lookup.operator, operator.pow)
        self.assertEqual(self.arith_lookup.operand, '15')
        self.assertEqual(self.arith_lookup.reverse, False)

    def test_config_mod(self):
        self.arith_lookup.config('%', '15')
        self.assertEqual(self.arith_lookup.operator, operator.mod)
        self.assertEqual(self.arith_lookup.operand, '15')
        self.assertEqual(self.arith_lookup.reverse, False)

    def test_config_unsupported(self):
        self.assertRaises(ValueError, self.arith_lookup.config, "&",
                          False, True)
        self.assertRaises(ValueError, self.arith_lookup.config, "**",
                          False, True)

    def test_call(self):
        self.arith_lookup.config('-', '10')
        self.assertEqual(5, self.arith_lookup(15))

    def test_call_reverse(self):
        self.arith_lookup.config('-', '10', True)
        self.assertEqual(-5, self.arith_lookup(15))

    def test_call_true_division(self):
        self.arith_lookup.config('/', '2')
        self.assertEqual(2.5, self.arith_lookup(5))

    def test_call_floor_division(self):
        self.arith_lookup.config('//', '2')
        self.assertEqual(2, self.arith_lookup(5))


class TestCustomLookup(unittest.TestCase):
    def test_shared_global_lut(self):
        class CustomLookup(BaseLookup):
            def config(self):
                self.expression = Expression(
                    'foo.bar',
                    fail_mode=FailMode.DEFAULT,
                    default=None,
                )

            def __call__(self, node, extra=None):
                return self.call_expression(self.expression, node, extra)

        data = {
            'foo': {
                'foo': {
                    'bar': 'foo',
                },
                'type': 'foo',
            },
            'bar': {
                'foo': {
                    'bar': 'bar',
                },
                'type': 'bar',
            }
        }

        lookup = CustomLookup().setup(expression='random')
        lut = {}

        first = lookup(data['foo'], {
            'root': data,
            'super_root': data,
            'lut': lut,
            'context': {}
        })
        second = lookup(data['bar'], {
            'root': data,
            'super_root': data,
            'lut': lut,
            'context': {}
        })

        self.assertEqual(first, 'foo'),
        self.assertEqual(second, 'bar'),
