# -*- coding: utf-8 -*-
"""Tests all functions in simplepath.utils"""
from __future__ import unicode_literals
import unittest

from simplepath.utils import deepvars


class Person(object):
    def __init__(self, phonebook, friends, non_friends, health):
        self.phonebook = phonebook
        self.friends = friends
        self.non_friends = non_friends
        self.health = health


class Friend(object):
    def __init__(self, name, birth_date):
        self.name = name
        self.birth_date = birth_date


class Health(object):
    __slots__ = ['weight', 'vision']

    def __init__(self, weight, vision):
        self.weight = weight
        self.vision = vision


class TestDeepVars(unittest.TestCase):
    """Tests simplepath.utils.deepvars."""

    def setUp(self):
        super(TestDeepVars, self).setUp()
        friends = [Friend('Goodluck Jonathan', '11/20/1957'),
                   Friend('Ibrahim Badamasi Babangida', '08/07/1941')]
        non_friends = ('Olusegun Obasanjo', 'Sani Abacha')
        self.test_health = Health(175, '20/20')
        phonebook = {'Babatunde Fashola': '+234-803-212-293-4805',
                     'Sullivan Chime': '+234-803-212-452-2039'}
        self.test_person = Person(phonebook, friends, non_friends,
                                  self.test_health)

    def test_object_dict_conversion(self):
        """Object with dictionaries, lists, tuples, and non-iterable
           objects as properties should be correctly converted to
           a dictionary.
        """
        expected = {
            'phonebook': {'Babatunde Fashola': '+234-803-212-293-4805',
                          'Sullivan Chime': '+234-803-212-452-2039'},
            'friends': [{'name': 'Goodluck Jonathan',
                         'birth_date': '11/20/1957'},
                        {'name': 'Ibrahim Badamasi Babangida',
                         'birth_date': '08/07/1941'}],
            'non_friends': ['Olusegun Obasanjo', 'Sani Abacha'],
            'health': {'weight': 175, 'vision': '20/20'}
        }
        self.assertDictEqual(expected,
                             deepvars(self.test_person))

    def test_object_slots_conversion(self):
        """Objects with __slots__ should return the appropriate
           data dictionary.
        """
        expected = {
            'weight': 175,
            'vision': '20/20'
        }
        self.assertDictEqual(expected,
                             deepvars(self.test_health))

    def test_non_object_conversion(self):
        """The same non-object element passed should be returned."""
        self.assertEqual(100, deepvars(100))
