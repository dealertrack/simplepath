# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

import mock
import six

from simplepath.constants import DEFAULT_FAIL_MODE, NONE, FailMode
from simplepath.exceptions import Skip
from simplepath.expressions import Expression
from simplepath.registry import LookupRegistry, registry


class TestExpression(unittest.TestCase):
    def setUp(self):
        super(TestExpression, self).setUp()

        with mock.patch.object(Expression, 'compile'):
            self.expression = Expression('foo.expression')

    def test_init_invalid_fail_mode(self):
        with self.assertRaises(AssertionError):
            Expression(None, fail_mode='foo')

    @mock.patch.object(Expression, 'compile')
    def test_init(self, mock_compile):
        expression = Expression('hello')

        self.assertEqual(expression.expression, 'hello')
        self.assertEqual(expression.default, NONE)
        self.assertEqual(expression.fail_mode, DEFAULT_FAIL_MODE)
        self.assertEqual(expression.registry, registry)
        mock_compile.assert_called_once_with()
        self.assertListEqual(expression, [])

    @mock.patch.object(Expression, 'compile')
    def test_init_no_compile(self, mock_compile):
        Expression('hello', do_compile=False)

        self.assertFalse(mock_compile.called)

    def test_copy_with(self):
        iterable = [
            mock.sentinel.one,
            mock.sentinel.two,
            mock.sentinel.three,
        ]

        actual = self.expression.copy_with(iterable)

        self.assertListEqual(actual, iterable)
        self.assertIsNot(actual, self.expression)

    def test_has_default(self):
        values = {
            NONE: False,
            None: True,
            0: True,
            '': True,
        }

        for k, expected in values.items():
            self.expression.default = k
            self.assertEqual(self.expression.has_default, expected)

    def test_compile(self):
        mock_lookup = mock.MagicMock()
        mock_animals = mock.MagicMock()
        self.expression.expression = 'foo.<animals:parrot,cat=dog>.bar'
        self.expression.registry = {
            None: mock_lookup,
            'animals': mock_animals,
        }

        self.expression.compile()

        self.assertListEqual(
            self.expression,
            [
                mock_lookup.return_value.setup.return_value,
                mock_animals.return_value.setup.return_value,
                mock_lookup.return_value.setup.return_value,
            ]
        )
        mock_lookup.assert_has_calls([
            mock.call(),
            mock.call().setup('foo', expression='foo'),
            mock.call(),
            mock.call().setup('bar', expression='bar'),
        ])
        mock_animals.assert_has_calls([
            mock.call(),
            mock.call().setup(
                'parrot',
                cat='dog',
                expression='<animals:parrot,cat=dog>'
            ),
        ])

    def test_compile_not_valid_lookup(self):
        mock_lookup = mock.MagicMock()
        self.expression.expression = 'foo.<animals:parrot,cat=dog>.bar'
        self.expression.registry = LookupRegistry(
            'my_registry', {
                None: mock_lookup,
            }
        )

        with self.assertRaises(KeyError) as e:
            self.expression.compile()

        self.assertIn('"animals" lookup is not registered in "my_registry"',
                      six.text_type(e.exception))

    def test_call(self):
        self.expression.expression = 'hello.world'
        mock_hello = mock.MagicMock(key='hello', expression='hello')
        mock_world = mock.MagicMock(key='world', expression='world',
                                    return_value='hi there')
        self.expression.extend([
            mock_hello,
            mock_world,
        ])
        lut = {'hello.world': 'hi there'}

        actual = self.expression(
            mock.sentinel.data,
            super_root=mock.sentinel.super_root,
            lut=lut,
            context={'some': 'stuff'},
        )

        self.assertEqual(actual, 'hi there')
        mock_hello.assert_called_once_with(
            mock.sentinel.data,
            extra={
                'root': mock.sentinel.data,
                'super_root': mock.sentinel.super_root,
                'lut': lut,
                'context': {'some': 'stuff'},
            }
        )

    def test_call_fail(self):
        self.expression.expression = 'hello.world'
        self.expression.fail_mode = FailMode.FAIL
        mock_hello = mock.MagicMock(key='hello', expression='hello',
                                    side_effect=KeyError)
        mock_world = mock.MagicMock(key='world', expression='world',
                                    return_value='hi there')
        self.expression.extend([
            mock_hello,
            mock_world,
        ])

        with self.assertRaises(KeyError):
            self.expression(
                mock.sentinel.data,
                lut={'hello.world': 'hi there'},
                context={'some': 'stuff'},
            )

    def test_call_no_default(self):
        self.expression.expression = 'hello.world'
        self.expression.default = NONE
        self.expression.fail_mode = FailMode.DEFAULT
        mock_hello = mock.MagicMock(key='hello', expression='hello',
                                    side_effect=KeyError)
        mock_world = mock.MagicMock(key='world', expression='world',
                                    return_value='hi there')
        self.expression.extend([
            mock_hello,
            mock_world,
        ])

        with self.assertRaises(KeyError):
            self.expression(
                mock.sentinel.data,
                lut={'hello.world': 'hi there'},
                context={'some': 'stuff'},
            )

    def test_call_with_default(self):
        self.expression.expression = 'hello.world'
        self.expression.default = None
        self.expression.fail_mode = FailMode.DEFAULT
        mock_hello = mock.MagicMock(key='hello', expression='hello',
                                    side_effect=KeyError)
        mock_world = mock.MagicMock(key='world', expression='world',
                                    return_value='hi there')
        self.expression.extend([
            mock_hello,
            mock_world,
        ])

        actual = self.expression(
            mock.sentinel.data,
            lut={'hello.world': 'hi there'},
            context={'some': 'stuff'},
        )

        self.assertIsNone(actual)

    def test_call_skip(self):
        self.expression.expression = 'hello.world'
        self.expression.fail_mode = FailMode.SKIP
        mock_hello = mock.MagicMock(key='hello', expression='hello',
                                    side_effect=KeyError)
        mock_world = mock.MagicMock(key='world', expression='world',
                                    return_value='hi there')
        self.expression.extend([
            mock_hello,
            mock_world,
        ])

        with self.assertRaises(Skip):
            self.expression(
                mock.sentinel.data,
                lut={'hello.world': 'hi there'},
                context={'some': 'stuff'},
            )

    def test_repr(self):
        self.expression.expression = 'hello.world'

        actual = repr(self.expression)

        self.assertEqual(
            actual,
            '<Expression expression="hello.world" chain=[]>'
        )
