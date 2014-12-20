from __future__ import unicode_literals

import six

from .constants import NONE
from .registry import registry


class Expression(list):
    def __init__(self, expression, default=NONE, lookup_registry=None):
        self.expression = expression
        self.default = default

        self.registry = lookup_registry or registry

        self.compile()

    @property
    def is_required(self):
        return self.default is NONE

    def compile(self):
        expressions = self.expression.split('.')

        for expression in expressions:
            # expressions like {name:value,key=value,key2=value}
            if all((expression.startswith('{'),
                    expression.endswith('}'))):
                _expression = expression[1:-1]
                # split expression to find name and arguments
                split = _expression.split(':', 1)
                name = split[0]
                args = []
                kwargs = {}

                # if split had more than one result, the rest are arguments
                if len(split) > 1:
                    for pairs in split[1].split('.'):
                        pair = pairs.split('=')
                        if len(pair) > 1:
                            kwargs.update(dict([pair]))
                        else:
                            args.append(pair[0])
                lookup = self.registry[name]().setup(
                    expression=expression, *args, **kwargs
                )

            else:
                lookup = self.registry[None]().setup(
                    expression, expression=expression
                )

            self.append(lookup)

    def __call__(self, data, lut):
        try:
            node = data
            for i, lookup in enumerate(self):
                chain_hash = '{}'.format('.'.join(map(
                    lambda i: six.text_type(i.expression),
                    self[:i + 1]
                )))
                if chain_hash in lut:
                    node = lut[chain_hash]
                else:
                    node = lookup(node, extra={'root': data})
                    lut[chain_hash] = node
        except (KeyError, IndexError):
            if self.is_required:
                raise
            return self.default
        else:
            return node

    def __repr__(self):
        return ('<{} expression="{}" chain=[{}]>'
                ''.format(self.__class__.__name__,
                          self.expression,
                          ','.join(repr(i) for i in self)))
