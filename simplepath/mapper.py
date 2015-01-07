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


class ListConfig(dict):
    """
    Public interface class for defining list mapper configs.

    For example::

        config = {
            'foo': ListConfig(
                'root_expression',
                {
                    'foo': 'expression',
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
        self.default = default
        self.fail_mode = fail_mode
        self.registry = lookup_registry or registry
        self.to_optimize = optimize

        self.update(self.compile(config))
        self.optimized = False
        if optimize:
            self.optimize()

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
        else:
            return Expression(node, **base_kwargs)

    def compile(self, config):
        return {
            k: self.compile_node(v)
            for k, v in config.items()
        }

    def _optimize(self, lut):
        for k, v in self.items():
            if isinstance(v, Value):
                continue

            elif isinstance(v, MapperListConfig):
                v.optimize()

            elif isinstance(v, MapperConfig):
                v._optimize(lut)

            else:
                optimized = None

                for i, e in enumerate(v):
                    chain_hash = '{}'.format('.'.join(map(
                        lambda l: l.expression,
                        v[:i + 1]
                    )))

                    if chain_hash in lut:
                        optimized = v.copy_with(
                            [LUTLookup().setup(expression=chain_hash,
                                               key=chain_hash)]
                            + v[i + 1:]
                        )
                    else:
                        lut[chain_hash] = None

                if optimized:
                    self[k] = optimized

    def optimize(self):
        lut = {}
        self._optimize(lut)
        self.optimized = True


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

    def map_node(self, node, data, super_root, lut):
        if isinstance(node, Value):
            return node.value

        elif isinstance(node, MapperListConfig):
            return self.map_list_node(node, data, super_root, lut)

        elif isinstance(node, MapperConfig):
            return self.map_config_node(node, data, super_root, lut)

        else:
            return node(
                data,
                super_root=super_root,
                lut=lut,
                context=self.get_lookup_context(),
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
