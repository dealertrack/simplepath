from __future__ import unicode_literals

from .chains import LookupChain
from .constants import NONE
from .registry import registry


class Expression(object):
    def __init__(self, expression, default=NONE, lookup_registry=None):
        self.expression = expression
        self.default = default

        self.registry = lookup_registry or registry
        self.chain = None

        self.compile()

    @property
    def is_required(self):
        return self.default is not NONE

    def compile(self):
        expressions = self.expression.split('.')
        self.chain = LookupChain(default=self.default)

        for expression in expressions:
            # expressions like {name:value,key=value,key2=value}
            if all((expression.startswith('{'),
                    expression.endswith('}'))):
                expression = expression[1:-1]
                # split expression to find name and arguments
                split = expression.split(':', 1)
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
                lookup = self.registry[name]().setup(*args, **kwargs)

            else:
                lookup = self.registry[None]().setup(expression)

            self.chain.append(lookup)

    def __repr__(self):
        return ('<{} expression="{}" chain=[{}]>'
                ''.format(self.__class__.__name__,
                          self.expression,
                          ','.join(repr(i) for i in self.chain)))
