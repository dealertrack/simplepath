from __future__ import unicode_literals

import six

from .constants import FailMode, NONE
from .exceptions import Skip
from .expressions import Expression
from .registry import registry


class ConfigCompiler(object):
    """
    Mapper configuration compiler which helps
    to build complied expressions tree.
    """

    def __init__(self, name, bases, attrs):
        self.name = name
        self.bases = bases
        self.attrs = attrs

    def get_attr(self, attr):
        if attr in self.attrs:
            return self.attrs[attr]

        for base in self.bases:
            try:
                return getattr(base, attr)
            except AttributeError:
                continue

        raise AttributeError(
            'None of the bases have {} attribute'
            ''.format(attr)
        )

    @property
    def config(self):
        expression = lambda v: (
            v
            if isinstance(v, Expression)
            else Expression(
                v,
                lookup_registry=self.get_attr('lookup_registry'),
                default=self.get_attr('default'),
                fail_mode=self.get_attr('fail_mode'),
            )
        )
        return {
            k: expression(v)
            for k, v in self.attrs['config'].items()
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
            'config': ConfigCompiler(name, bases, attrs).config,
        })

        return _super(cls, name, bases, attrs)


class MapperBase(object):
    """
    Base mapper class.

    This class implements the actual mapping functionality.
    """
    default = NONE
    fail_mode = FailMode.FAIL_IF_REQUIRED
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

    def __call__(self, data):
        output = {}
        for key, expression in self.config.items():
            try:
                output[key] = expression(
                    data,
                    lut=self.lut,
                    context=self.get_lookup_context(),
                )
            except Skip:
                pass
        return output


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
