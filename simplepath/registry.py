# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .lookups import FindInListLookup, KeyLookup


class LookupRegistry(dict):
    def __init__(self, name, *args, **kwargs):
        super(LookupRegistry, self).__init__(*args, **kwargs)
        self.name = name

    def register(self, name, lookup):
        self[name] = lookup


registry = LookupRegistry('simplepath.registry')

# register built-in lookups
registry.register(None, KeyLookup)
registry.register('find', FindInListLookup)
