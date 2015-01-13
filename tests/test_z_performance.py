# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import sys
import unittest
from functools import partial

import six
from contexttimer import Timer
from nose.plugins.attrib import attr

from simplepath.mapper import SimpleMapper


err_print = partial(print, file=sys.stderr)


@attr('slow')
class TestMapperPerformance(unittest.TestCase):
    def _generate_config(self, nodes=2, depth=2):
        def _generate(nodes, depth, data=[], iteration=0):
            if iteration == depth:
                return [
                    '{}.foo'.format(i)
                    for i in data
                ]

            _data = [
                'foo{}.<find:value={}>.foo{}'.format(i, j, k)
                for i in range(nodes)
                for j in range(nodes)
                for k in range(nodes)
            ]

            if not data:
                data = _data
            else:
                data = [
                    '{}.{}'.format(i, j)
                    for i in data
                    for j in _data
                ]

            return _generate(
                nodes=nodes,
                depth=depth,
                data=data,
                iteration=iteration + 1,
            )

        return {
            '{:05}'.format(i): v
            for i, v in enumerate(_generate(nodes, depth / 2))
        }

    def _generate_data(self, nodes=2, depth=2, iteration=0):
        # count recursion from 0 and depth provides recursion limit
        if iteration == depth:
            return {'foo': 'bar'}

        output = {}
        for i in range(nodes):
            # every other level return list of data
            if not iteration % 2:
                data = []
                for j in range(nodes):
                    _data = self._generate_data(
                        nodes=nodes,
                        depth=depth,
                        iteration=iteration + 1
                    )
                    _data['value'] = six.text_type(j)
                    data.append(_data)
            else:
                data = (
                    self._generate_data(
                        nodes=nodes,
                        depth=depth,
                        iteration=iteration + 1,
                    )
                )
            output['foo{}'.format(i)] = data
        return output

    def _test_performance(self,
                          nodes,
                          depth,
                          iterations,
                          optimize):
        err_print()
        err_print('Testing performance with {} config expressions '
                  'where each node has {} children '
                  'with depth of {}'
                  ''.format(int((nodes ** 3) ** (depth / 2)),
                            nodes,
                            depth))

        with Timer() as timer:
            data = self._generate_data(nodes=nodes, depth=depth)
        err_print('Generated data in {} sec'.format(timer.elapsed))

        with Timer() as timer:
            config = self._generate_config(nodes=nodes, depth=depth)
        err_print('Generated config in {} sec'.format(timer.elapsed))

        with Timer() as timer:
            mapper = SimpleMapper(config, optimize=optimize)
        err_print('Compiled {} config expressions in {} sec'
                  ''.format(len(config), timer.elapsed))

        times = []
        for i in range(iterations):
            with Timer() as map_timer:
                _mapper = mapper()
                mapped_data = _mapper(data)
            times.append(map_timer.elapsed)
        err_print('Mapped {} nodes in [{}] sec'
                  ''.format(len(mapped_data),
                            ','.join(map(six.text_type, times))))
        err_print('Total lookups: {}'
                  ''.format(sum(map(lambda i: len(i),
                                    _mapper.config.values()))))
        err_print('LUT entries: {}'.format(len(_mapper.lut)))
        err_print('LUT reads: {}'.format(_mapper.lut.reads))
        err_print('LUT writes: {}'.format(_mapper.lut.writes))

    def test_performance_deep(self):
        self._test_performance(
            nodes=3, depth=6, iterations=3, optimize=False,
        )

    def test_performance_deep_optimized(self):
        self._test_performance(
            nodes=3, depth=6, iterations=3, optimize=True,
        )

    def test_performance_shallow(self):
        self._test_performance(
            nodes=10, depth=2, iterations=3, optimize=False,
        )

    def test_performance_shallow_optimized(self):
        self._test_performance(
            nodes=10, depth=2, iterations=3, optimize=True,
        )
