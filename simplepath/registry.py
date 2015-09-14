# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .lookups import (
    ArithmeticLookup,
    AsTypeLookup,
    FindInListLookup,
    KeyLookup,
)


class LookupRegistry(dict):
    def __init__(self, name, *args, **kwargs):
        super(LookupRegistry, self).__init__(*args, **kwargs)
        self.name = name

    def register(self, name, lookup):
        self[name] = lookup


registry = LookupRegistry('simplepath.registry')

# register built-in lookups
registry.register(None, KeyLookup)
registry.register('arith', ArithmeticLookup)
registry.register('as_type', AsTypeLookup)
registry.register('find', FindInListLookup)
