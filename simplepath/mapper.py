from __future__ import unicode_literals

from .expressions import Expression


class Mapper(object):
    def __init__(self, config):
        self.config = {
            k: v if isinstance(v, Expression) else Expression(v)
            for k, v in config.items()
        }

    def __call__(self, data):
        output = {}
        for key, expression in self.config.items():
            output[key] = expression.chain.eval(data)
        return output
