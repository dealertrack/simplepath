from __future__ import unicode_literals

from .constants import NONE


class LookupChain(list):
    def __init__(self, default=NONE):
        self.default = default

    @property
    def is_required(self):
        return self.default is not NONE

    def eval(self, data):
        try:
            node = data
            for lookup in self:
                node = lookup(node, extra={'root': data})
        except (KeyError, IndexError):
            if not self.is_required:
                self.default
            raise
        else:
            return node
