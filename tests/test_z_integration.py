# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from simplepath.mapper import ListConfig, Mapper, Value


class TestIntegration(unittest.TestCase):
    def test_everything(self):
        class Config(Mapper):
            config = {
                'greetings': 'example.greetings',
                'from': Value('friends'),
                'to': 'example.planets.<find:planet=Earth>.residents',
                'neighbors': ListConfig(
                    'example.planets',
                    {
                        'from': 'planet',
                        'neighbors': 'residents',
                    },
                ),
            }

        data = {
            'example': {
                'greetings': 'Hello',
                'planets': [
                    {
                        'planet': 'Mars',
                        'residents': 'marsians',
                    },
                    {
                        'planet': 'Earth',
                        'residents': 'people',
                    },
                    {
                        'planet': 'Space',
                        'residents': 'aliens',
                    },
                ]
            }
        }
        expected = {
            'greetings': 'Hello',
            'from': 'friends',
            'to': 'people',
            'neighbors': [
                {
                    'from': 'Mars',
                    'neighbors': 'marsians',
                },
                {
                    'from': 'Earth',
                    'neighbors': 'people',
                },
                {
                    'from': 'Space',
                    'neighbors': 'aliens',
                }
            ]
        }

        self.assertDictEqual(Config.map_data(data), expected)
