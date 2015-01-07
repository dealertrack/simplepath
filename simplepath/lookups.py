# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class BaseLookup(object):
    def config(self, *args, **kwargs):
        pass

    def setup(self, *args, **kwargs):
        self.expression = kwargs.pop('expression')
        self.config(*args, **kwargs)
        return self

    def repr(self):
        return ''

    def call_expression(self, expression, data, extra):
        return expression(
            data,
            super_root=extra.get('super_root'),
            lut=extra.get('lut'),
            context=extra.get('context'),
        )

    def __call__(self, node, extra=None):
        raise NotImplementedError

    def __repr__(self):
        return (
            '<{} {}>'.format(
                self.__class__.__name__,
                self.repr(),
            )
        )


class KeyLookup(BaseLookup):
    def config(self, key):
        self.key = key

    def __call__(self, node, extra=None):
        if isinstance(node, (list, tuple)):
            return node[int(self.key)]
        else:
            return node[self.key]

    def repr(self):
        return 'key="{}"'.format(self.key)


class FindInListLookup(BaseLookup):
    def config(self, **conditions):
        self.conditions = conditions

    def __call__(self, nodes, extra=None):
        for node in nodes:
            present = {k: node.get(k) for k in self.conditions}
            if present == self.conditions:
                return node
        raise ValueError('Not found any node matching all conditions')

    def repr(self):
        return ', '.join(
            '{}="{}"'.format(k, v)
            for k, v in self.conditions.items()
        )


class LUTLookup(KeyLookup):
    def __call__(self, node, extra=None):
        return extra['lut'][self.key]
