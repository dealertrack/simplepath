# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six

from .constants import DEFAULT_FAIL_MODE, FailMode, NONE
from .exceptions import Skip
from .expressions import Expression
from .registry import registry


class MapperConfig(dict):
    """
    Mapper configuration helper class which mimics a dictionary
    however recursively compiles all subdictionaries.
    """

    def __init__(self,
                 config,
                 default=NONE,
                 fail_mode=DEFAULT_FAIL_MODE,
                 lookup_registry=None):
        self.default = default
        self.fail_mode = fail_mode
        self.registry = lookup_registry or registry

        self.update(self.compile(config))

    def compile_node(self, node):
        kwargs = dict(
            default=self.default,
            fail_mode=self.fail_mode,
            lookup_registry=self.registry,
        )

        if isinstance(node, Expression):
            return node
        elif isinstance(node, dict):
            return MapperConfig(node, **kwargs)
        else:
            return Expression(node, **kwargs)

    def compile(self, config):
        return {
            k: self.compile_node(v)
            for k, v in config.items()
        }


class MapperMeta(type):
    """
    Mapper metaclass.

    This metalcass compiles configuration for performance.
    By doing that during class creation it allows class
    to simply use conpiled configuration at run-time and not
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

    def __init__(self):
        self.lut = {}

    @classmethod
    def map_data(self, data):
        """
        Shortcut for mapping data which does not require
        to instantiate class in order to map data.
        """
        return self()(data)

    def get_lookup_context(self):
        return {}

    def map_node(self, node):
        if isinstance(node, dict):
            output = {}
            for key, node in node.items():
                try:
                    output[key] = self.map_node(node)
                except Skip:
                    pass
            return output

        else:
            return node(
                self.data,
                lut=self.lut,
                context=self.get_lookup_context(),
            )

    def __call__(self, data):
        self.data = data
        return self.map_node(self.config)


class Mapper(six.with_metaclass(MapperMeta, MapperBase)):
    """
    Interface mapper class.

    All mappers should subclass this class to create
    mappers with specific configurations.
    """


def SimpleMapper(config, **attrs):
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
    return type(str('Mapper'), (Mapper,), attrs)


def map_data(config, data, **attrs):
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
    return SimpleMapper(config, **attrs).map_data(data)
