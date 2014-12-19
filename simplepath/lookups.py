from __future__ import unicode_literals


class BaseLookup(object):
    def config(self, *args, **kwargs):
        pass

    def setup(self, *args, **kwargs):
        self.config(*args, **kwargs)
        return self

    def __call__(self, node, extra=None):
        raise NotImplementedError


class KeyLookup(BaseLookup):
    def config(self, key):
        self.key = key

    def __call__(self, node, extra=None):
        if isinstance(node, (list, tuple)):
            return node[int(self.key)]
        else:
            return node[self.key]


class FindInListLookup(BaseLookup):
    def config(self, **conditions):
        self.conditions = conditions

    def __call__(self, nodes, extra=None):
        for node in nodes:
            present = {k: node[k] for k in self.conditions}
            if present == self.conditions:
                return node
        raise ValueError('Not found any node matching all conditions')
