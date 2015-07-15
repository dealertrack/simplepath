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
                'owning': [
                    'cool_object',
                    Value('with'),
                    Value('Ion Engine'),
                ],
            }

        data = {
            'example': {
                'greetings': 'Hello',
                'planets': [
                    {
                        'planet': 'Mars',
                        'residents': 'martians',
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
            },
            'cool_object': 'Space Shuttle',
        }
        expected = {
            'greetings': 'Hello',
            'from': 'friends',
            'to': 'people',
            'neighbors': [
                {
                    'from': 'Mars',
                    'neighbors': 'martians',
                },
                {
                    'from': 'Earth',
                    'neighbors': 'people',
                },
                {
                    'from': 'Space',
                    'neighbors': 'aliens',
                }
            ],
            'owning': [
                'Space Shuttle',
                'with',
                'Ion Engine',
            ]
        }

        self.assertDictEqual(Config.map_data(data), expected)
