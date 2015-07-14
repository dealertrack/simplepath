# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six

from .constants import DEFAULT_FAIL_MODE, DELIMITERS, NONE, FailMode
from .exceptions import Skip
from .registry import registry


class Expression(list):
    def __init__(self,
                 expression,
                 default=NONE,
                 fail_mode=DEFAULT_FAIL_MODE,
                 lookup_registry=None,
                 do_compile=True):
        super(Expression, self).__init__()

        assert FailMode.is_valid(fail_mode), (
            'fail_mode "{}" is not supported'
            ''.format(fail_mode)
        )

        self.expression = expression

        self.default = default
        self.fail_mode = fail_mode
        self.registry = lookup_registry or registry

        if do_compile:
            self.compile()

    def copy_with(self, iterable):
        copy = self.__class__(
            expression=self.expression,
            default=self.default,
            fail_mode=self.fail_mode,
            lookup_registry=self.registry,
            do_compile=False,
        )
        copy.extend(iterable)
        return copy

    @property
    def has_default(self):
        return self.default is not NONE

    def compile(self):
        expressions = self.expression.split(DELIMITERS['expression'])

        for expression in expressions:
            # expressions like {name:value,key=value,key2=value}
            if all((expression.startswith(DELIMITERS['lookup']['start']),
                    expression.endswith(DELIMITERS['lookup']['end']))):
                _expression = expression[
                    len(DELIMITERS['lookup']['start']):
                    -len(DELIMITERS['lookup']['end'])
                ]
                # split expression to find name and arguments
                split = _expression.split(':', 1)
                name = split[0]
                args = []
                kwargs = {}

                # if split had more than one result, the rest are arguments
                if len(split) > 1:
                    for pairs in split[1].split(','):
                        pair = pairs.split('=')
                        if len(pair) > 1:
                            kwargs.update(dict([pair]))
                        else:
                            args.append(pair[0])

                if name not in self.registry:
                    registered = [i for i in self.registry.keys() if i]
                    raise KeyError(
                        '"{name}" lookup is not registered in "{registry}". '
                        'Currently registered lookups are "{registered}". '
                        'Please make sure to register all custom lookups '
                        'before compiling expressions.'
                        ''.format(name=name,
                                  registry=self.registry.name,
                                  registered=', '.join(registered))
                    )

                lookup = self.registry[name]().setup(
                    expression=expression, *args, **kwargs
                )

            else:
                lookup = self.registry[None]().setup(
                    expression, expression=expression
                )

            self.append(lookup)

    def __call__(self, data, super_root=None, lut=None, context=None):
        lut = lut if lut is not None else {}
        context = context if context is not None else {}
        super_root = super_root if super_root is not None else data

        try:
            node = data
            for i, lookup in enumerate(self):
                chain_hash = '{}'.format('.'.join(map(
                    lambda l: six.text_type(l.expression),
                    self[:i + 1]
                )))
                if chain_hash in lut:
                    node = lut[chain_hash]
                else:
                    extra = {
                        'root': data,
                        'super_root': super_root,
                        'lut': lut,
                        'context': context,
                    }
                    node = lookup(node, extra=extra)
                    lut[chain_hash] = node

        except Exception:
            if any((self.fail_mode == FailMode.FAIL,
                    self.fail_mode == FailMode.DEFAULT
                    and not self.has_default)):
                raise
            if self.fail_mode == FailMode.SKIP:
                raise Skip
            return self.default

        else:
            return node

    def __repr__(self):
        return ('<{} expression="{}" chain=[{}]>'
                ''.format(self.__class__.__name__,
                          self.expression,
                          ','.join(repr(i) for i in self)))
