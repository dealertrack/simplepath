# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .lookups import FindInListLookup, KeyLookup


class LookupRegistry(dict):
    def register(self, name, lookup):
        self[name] = lookup


registry = LookupRegistry()

# register built-in lookups
registry.register(None, KeyLookup)
registry.register('find', FindInListLookup)
