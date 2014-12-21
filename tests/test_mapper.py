# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from collections import OrderedDict

import mock
import six

from simplepath.exceptions import Skip
from simplepath.expressions import Expression
from simplepath.mapper import (
    Mapper,
    MapperBase,
    MapperConfig,
    MapperMeta,
    SimpleMapper,
    map_data,
)


TESTING_MODULE = 'simplepath.mapper'


class TestMapperConfig(unittest.TestCase):
    @mock.patch.object(MapperConfig, 'optimize')
    @mock.patch.object(MapperConfig, 'compile')
    def setUp(self, mock_compile, mock_optimize):
        super(TestMapperConfig, self).setUp()

        mock_compile.return_value = {}
        self.config = MapperConfig(None)

    @mock.patch.object(MapperConfig, 'optimize')
    @mock.patch.object(MapperConfig, 'compile')
    def test_init(self, mock_compile, mock_optimize):
        mock_compile.return_value = {
            'foo': 'bar',
        }

        config = MapperConfig(mock.sentinel.config)

        self.assertDictEqual(
            config,
            {'foo': 'bar'}
        )
        mock_compile.assert_called_once_with(mock.sentinel.config)
        mock_optimize.assert_called_once_with()

    @mock.patch.object(MapperConfig, 'compile_node')
    def test_compile(self, mock_compile_node):
        actual = self.config.compile({'foo': 'bar'})

        self.assertDictEqual(
            actual,
            {'foo': mock_compile_node.return_value}
        )
        mock_compile_node.assert_called_once_with('bar')

    def test_compile_node(self):
        node = mock.MagicMock(spec=Expression)

        actual = self.config.compile_node(node)

        self.assertIs(actual, node)

    @mock.patch(TESTING_MODULE + '.MapperConfig')
    def test_compile_node_recursive(self, mock_mapper_config):
        node = mock.MagicMock(spec=dict)

        actual = self.config.compile_node(node)

        self.assertEqual(actual, mock_mapper_config.return_value)
        mock_mapper_config.assert_called_once_with(
            node,
            default=mock.ANY,
            fail_mode=mock.ANY,
            lookup_registry=mock.ANY,
        )

    @mock.patch.object(Expression, '__init__')
    def test_compile_node_expression(self, mock_expression):
        mock_expression.return_value = None
        node = mock.MagicMock()

        actual = self.config.compile_node(node)

        self.assertIsInstance(actual, Expression)
        mock_expression.assert_called_once_with(
            node,
            default=mock.ANY,
            fail_mode=mock.ANY,
            lookup_registry=mock.ANY,
        )

    def test__optimize_recursive(self):
        node = mock.MagicMock(spec=MapperConfig)
        self.config.update({
            'foo': node,
        })

        self.config._optimize(mock.sentinel.lut)

        node._optimize.assert_called_once_with(mock.sentinel.lut)

    @mock.patch(TESTING_MODULE + '.LUTLookup')
    def test__optimize(self, mock_lut_lookup):
        class Foo(list):
            copy_with = mock.MagicMock()

        node1 = mock.MagicMock(expression='hi')
        node2 = mock.MagicMock(expression='hello')
        self.config.update({
            'foo': Foo([node1, node2]),
        })
        lut = {'hi': 'there'}

        self.config._optimize(lut)

        self.assertDictEqual(
            self.config,
            {
                'foo': Foo.copy_with.return_value,
            }
        )
        Foo.copy_with.assert_called_once_with([
            mock_lut_lookup.return_value.setup.return_value,
            node2,
        ])
        mock_lut_lookup.return_value.setup.assert_called_once_with(
            expression='hi', key='hi',
        )

    @mock.patch.object(MapperConfig, '_optimize')
    def test_optimize(self, mock_optimize):
        self.assertFalse(self.config.optimized)

        self.config.optimize()

        self.assertTrue(self.config.optimized)
        mock_optimize.assert_called_once_with({})


class TestMapperMeta(unittest.TestCase):
    @mock.patch(TESTING_MODULE + '.MapperConfig')
    @mock.patch.object(MapperMeta, 'get_attr')
    def test_new_base(self, mock_get_attr, mock_mapper_config):
        @six.add_metaclass(MapperMeta)
        class Foo(object):
            pass

        self.assertFalse(mock_mapper_config.called)

    @mock.patch(TESTING_MODULE + '.MapperConfig')
    @mock.patch.object(MapperMeta, 'get_attr')
    def test_new(self, mock_get_attr, mock_mapper_config):
        @six.add_metaclass(MapperMeta)
        class Foo(object):
            config = mock.sentinel.config

        self.assertEqual(Foo.config, mock_mapper_config.return_value)
        mock_mapper_config.assert_called_once_with(
            mock.sentinel.config,
            default=mock_get_attr.return_value,
            fail_mode=mock_get_attr.return_value,
            lookup_registry=mock_get_attr.return_value,
            optimize=mock_get_attr.return_value,
        )
        mock_get_attr.assert_has_calls([
            mock.call(mock.ANY, mock.ANY, 'default'),
            mock.call(mock.ANY, mock.ANY, 'fail_mode'),
            mock.call(mock.ANY, mock.ANY, 'lookup_registry'),
        ])

    def test_get_attr_in_attrs(self):
        actual = MapperMeta.get_attr(tuple(), {'foo': 'bar'}, 'foo')

        self.assertEqual(actual, 'bar')

    def test_get_attr_not_in_bases(self):
        with self.assertRaises(AttributeError):
            MapperMeta.get_attr(tuple(), {}, 'foo')

    def test_get_attr_in_bases(self):
        bases = (
            object(),
            mock.MagicMock(foo='bar')
        )

        actual = MapperMeta.get_attr(bases, {}, 'foo')

        self.assertEqual(actual, 'bar')


class TestMapperBase(unittest.TestCase):
    def setUp(self):
        super(TestMapperBase, self).setUp()
        self.mapper = MapperBase()
        self.mapper.config = {}

    def test_init(self):
        actual = MapperBase()

        self.assertDictEqual(actual.lut, {})

    def test_get_lookup_context(self):
        self.assertDictEqual(self.mapper.get_lookup_context(), {})

    @mock.patch.object(MapperBase, 'map_node')
    def test_call(self, mock_map_node):
        self.mapper(mock.sentinel.data)

        self.assertEqual(self.mapper.data, mock.sentinel.data)
        mock_map_node.assert_called_once_with(self.mapper.config)

    @mock.patch.object(MapperBase, '__call__')
    def test_map_data(self, mock_call):
        actual = MapperBase.map_data(mock.sentinel.data)

        self.assertEqual(actual, mock_call.return_value)
        mock_call.assert_called_once_with(mock.sentinel.data)

    @mock.patch.object(MapperBase, 'get_lookup_context')
    def test_map_node(self, mock_get_lookup_context):
        node = mock.MagicMock()
        self.mapper.data = mock.sentinel.data

        actual = self.mapper.map_node(node)

        self.assertEqual(actual, node.return_value)
        node.assert_called_once_with(
            mock.sentinel.data,
            lut=self.mapper.lut,
            context=mock_get_lookup_context.return_value,
        )

    def test_map_node_recursive(self):
        method = self.mapper.map_node
        node = OrderedDict((
            ('foo', mock.sentinel.foo),
            ('bar', mock.sentinel.bar),
        ))
        bar = mock.MagicMock()

        # mocking inside to test recursion
        with mock.patch.object(MapperBase, 'map_node') as mock_map_node:
            mock_map_node.side_effect = Skip, bar
            actual = method(node)

        self.assertDictEqual(actual, {'bar': bar})
        mock_map_node.assert_has_calls([
            mock.call(mock.sentinel.foo),
            mock.call(mock.sentinel.bar),
        ])


class TestHelpers(unittest.TestCase):
    @mock.patch(TESTING_MODULE + '.type', create=True)
    def test_simple_mapper(self, mock_type):
        actual = SimpleMapper(mock.sentinel.config, foo='bar')

        self.assertEqual(actual, mock_type.return_value)
        mock_type.assert_called_once_with(
            str('Mapper'),
            (Mapper,),
            {
                'config': mock.sentinel.config,
                'foo': 'bar',
            }
        )

    @mock.patch(TESTING_MODULE + '.SimpleMapper')
    def test_map_data(self, mock_simple_mapper):
        actual = map_data(mock.sentinel.config,
                          mock.sentinel.data,
                          foo='bar')

        self.assertEqual(
            actual,
            (mock_simple_mapper.return_value
             .map_data.return_value)
        )
        mock_simple_mapper.assert_called_once_with(
            mock.sentinel.config, foo='bar',
        )
        mock_simple_mapper.return_value.map_data.assert_called_once_with(
            mock.sentinel.data,
        )
