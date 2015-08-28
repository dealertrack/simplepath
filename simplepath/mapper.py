# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six

from .constants import DEFAULT_FAIL_MODE, NONE
from .exceptions import Skip
from .expressions import Expression
from .lookups import LUTLookup
from .lut import LUT
from .registry import registry


class Value(object):
    """
    Public interface class for allowing to include hardcoded values
    in configs vs adding lookups.
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<{} value="{}">'.format(self.__class__.__name__, self.value)


class ListConfig(dict):
    """
    Public interface class for defining list mapper configs.

    It is used to return a list of dictionaries based on the value in the
    root_expression. It is analogous to map(func, list) in which the
    func's return value is the mapping, and the list is the final node
    in the root expression.

    For example::

        config = {
            'new_key': ListConfig(
                'root_expression',
                {
                    'key1': 'expression1',
                    'key2': 'expression2',
                     ...
                    'keyN': 'expressionN',
                }
            )
        }
    """

    def __init__(self, root, config):
        self.root = root
        super(ListConfig, self).__init__(config)


class MapperConfig(dict):
    """
    Mapper configuration helper class which mimics a dictionary
    however recursively compiles all subdictionaries.
    """

    def __init__(self,
                 config,
                 default=NONE,
                 fail_mode=DEFAULT_FAIL_MODE,
                 lookup_registry=None,
                 optimize=True):
        super(MapperConfig, self).__init__()

        self.default = default
        self.fail_mode = fail_mode
        self.registry = lookup_registry or registry
        self.to_optimize = optimize

        self.update(self.compile(config))
        self.optimized = False
        if optimize:
            self.run_optimization()

    def compile_node(self, node):
        base_kwargs = dict(
            default=self.default,
            fail_mode=self.fail_mode,
            lookup_registry=self.registry,
        )
        mapper_kwargs = base_kwargs.copy()
        mapper_kwargs.update({
            'optimize': False,
        })

        if isinstance(node, Expression):
            return node
        elif isinstance(node, Value):
            return node
        elif isinstance(node, ListConfig):
            return MapperListConfig(node.root, node, **mapper_kwargs)
        elif isinstance(node, dict):
            return MapperConfig(node, **mapper_kwargs)
        elif isinstance(node, list):
            return [self.compile_node(i) for i in node]
        else:
            return Expression(node, **base_kwargs)

    def compile(self, config):
        return {
            k: self.compile_node(v)
            for k, v in config.items()
        }

    def _optimize_value(self, node, lut):
        return node

    def _optimize_list_config(self, node, lut):
        # list lut namespace cannot interfere with
        return node.run_optimization()

    def _optimize_mapper_config(self, node, lut):
        return node.optimize(lut)

    def _optimize_expression(self, node, lut):
        optimized = None

        for i, e in enumerate(node):
            chain_hash = '{}'.format('.'.join(map(
                lambda l: l.expression,
                node[:i + 1]
            )))

            if chain_hash in lut:
                optimized = node.copy_with(
                    [LUTLookup().setup(expression=chain_hash,
                                       key=chain_hash)]
                    + node[i + 1:]
                )
            else:
                # mark the expression as available in the lut
                # so that other expressions can be aware
                # that a particular value will be computed by
                # a different expression
                lut[chain_hash] = None

        return optimized or node

    def _optimize_list(self, node, lut):
        return [self._optimize(i, lut) for i in node]

    def _optimize(self, node, lut):
        if isinstance(node, Value):
            return self._optimize_value(node, lut)

        elif isinstance(node, MapperListConfig):
            return self._optimize_list_config(node, lut)

        elif isinstance(node, MapperConfig):
            return self._optimize_mapper_config(node, lut)

        elif isinstance(node, Expression):
            return self._optimize_expression(node, lut)

        elif isinstance(node, list):
            return self._optimize_list(node, lut)

        else:
            raise TypeError(
                'Why are you even here? '
                'Were you looking at your type map upside down? '
                '"{}" is not even on the map.'
                ''.format(type(node))
            )

    def optimize(self, lut):
        for k in list(self.keys()):
            self[k] = self._optimize(self[k], lut)
        return self

    def run_optimization(self):
        lut = {}
        self.optimize(lut)
        self.optimized = True
        return self


class MapperListConfig(MapperConfig):
    """
    Mapper configuration to compile configs provided as ListConfig
    """

    def __init__(self, root, *args, **kwargs):
        super(MapperListConfig, self).__init__(*args, **kwargs)
        # has to be after main __init__ for compile to work
        self.root = self.compile_node(root)


class MapperMeta(type):
    """
    Mapper metaclass.

    This metaclass compiles configuration for performance.
    By doing that during class creation it allows class
    to simply use compiled configuration at run-time and not
    waste time parsing configuration expressions.
    """

    def __new__(cls, name, bases, attrs):
        _super = super(MapperMeta, cls).__new__

        # if config is not provided, one of the base
        # classes themselves is probably being created
        # in which case simply return class itself
        if 'config' not in attrs:
            return _super(cls, name, bases, attrs)

        attrs.update({
            'config': MapperConfig(
                attrs['config'],
                default=cls.get_attr(bases, attrs, 'default'),
                fail_mode=cls.get_attr(bases, attrs, 'fail_mode'),
                lookup_registry=cls.get_attr(bases, attrs, 'lookup_registry'),
                optimize=cls.get_attr(bases, attrs, 'optimize'),
            ),
        })

        return _super(cls, name, bases, attrs)

    @classmethod
    def get_attr(cls, bases, attrs, attr):
        if attr in attrs:
            return attrs[attr]

        for base in bases:
            try:
                return getattr(base, attr)
            except AttributeError:
                continue

        raise AttributeError(
            'None of the bases have {} attribute'
            ''.format(attr)
        )


class MapperBase(object):
    """
    Base mapper class.

    This class implements the actual mapping functionality.
    """
    default = NONE
    fail_mode = DEFAULT_FAIL_MODE
    lookup_registry = registry
    optimize = True

    def __init__(self):
        self.lut = LUT()

    @classmethod
    def map_data(cls, data):
        """
        Shortcut for mapping data which does not require
        to instantiate class in order to map data.
        """
        return cls()(data)

    def get_lookup_context(self):
        return {}

    def map_expression(self, node, data, super_root, lut):
        return node(
            data,
            super_root=super_root,
            lut=lut,
            context=self.get_lookup_context(),
        )

    def map_list_node(self, node, data, super_root, lut):
        output = []

        # please note that we are not catching Skip exception here
        # the reason being that map_list_node is called within
        # map_config_node anyway which does catch it
        input_list = node.root(
            data,
            super_root=super_root,
            lut=lut,
            context=self.get_lookup_context(),
        )

        for value in input_list:
            # due to relative lookups, cannot use main lut
            output.append(self.map_config_node(node, value, super_root, {}))

        return output

    def map_config_node(self, node, data, super_root, lut):
        output = {}

        for key, node in node.items():
            try:
                output[key] = self.map_node(node, data, super_root, lut)
            except Skip:
                pass

        return output

    def map_list(self, node, data, super_root, lut):
        return [self.map_node(i, data, super_root, lut) for i in node]

    def map_node(self, node, data, super_root, lut):
        if isinstance(node, Value):
            return node.value

        elif isinstance(node, MapperListConfig):
            return self.map_list_node(node, data, super_root, lut)

        elif isinstance(node, MapperConfig):
            return self.map_config_node(node, data, super_root, lut)

        elif isinstance(node, Expression):
            return self.map_expression(node, data, super_root, lut)

        elif isinstance(node, list):
            return self.map_list(node, data, super_root, lut)

        else:
            raise TypeError(
                '"{}" does not quality for free ice-cream.'
                ''.format(type(node))
            )

    def __call__(self, data):
        self.data = data
        return self.map_node(self.config, self.data, self.data, self.lut)


class Mapper(six.with_metaclass(MapperMeta, MapperBase)):
    """
    Interface mapper class.

    All mappers should subclass this class to create
    mappers with specific configurations.
    """


def SimpleMapper(config, base_mapper=None, **attrs):
    """
    Simple function wrapper for creating mapper class.

    This allows to create dynamic mappers simply by calling
    a function vs creating ad-hoc class.

    Examples
    --------

    These are identical::

        class MyMapper(Mapper):
            config = {
                'foo': 'bar',
            }

        MyMapper = SimpleMapper({'foo': 'bar'})
    """
    attrs.update({
        'config': config,
    })
    return type(str('Mapper'), (base_mapper or Mapper,), attrs)


def map_data(config, data, base_mapper=None, **attrs):
    """
    Method for mapping data using provided configuration.

    .. note:: This method is not efficient since on every single
        call it compiles the provided configuration. If you
        need to map data with same configuration multiple times,
        please create a dedicated mapper class which will compile
        configuration once. That will allow for best possible
        performance. For example::

            mapper = SimpleMapper(config)
            mapped1 = mapper.map_data(data1)
            mapped2 = mapper.map_data(data2)
    """
    return SimpleMapper(config, base_mapper, **attrs).map_data(data)
