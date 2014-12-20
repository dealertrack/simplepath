from __future__ import unicode_literals

from .expressions import Expression


class MapperConfig(dict):
    def __init__(self, config):
        self.update({
            k: v if isinstance(v, Expression) else Expression(v)
            for k, v in config.items()
        })


class Mapper(object):
    def __init__(self, config):
        self.config = config

    def __call__(self, data):
        output = {}
        lut = {}
        for key, expression in self.config.items():
            output[key] = expression.eval(data, lut)
        return output
