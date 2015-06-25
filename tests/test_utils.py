"""Tests all functions in simplepath.utils"""
import unittest


from simplepath.utils import convert_object_to_dict


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
    def __init__(self, weight, vision):
        self.weight = weight
        self.vision = vision


class TestConvertObjectToDict(unittest.TestCase):
    """Tests simplepath.utils.convert_object_to_dict."""

    def setUp(self):
        super(TestConvertObjectToDict, self).setUp()
        friends = [Friend("Goodluck Jonathan", "11/20/1957"),
                   Friend("Ibrahim Badamasi Babangida", "08/07/1941")]
        non_friends = ("Olusegun Obasanjo", "Sani Abacha")
        health = Health(175, "20/20")
        phonebook = {"Babatunde Fashola": "+234-803-212-293-4805",
                     "Sullivan Chime": "+234-803-212-452-2039"}
        self.test_person = Person(phonebook, friends, non_friends, health)

    def test_object_conversion(self):
        """Object with dictionaries, lists, tuples, and non-iterable
           objects as properties should be correctly converted to
           a dictionary.
        """
        expected = {
            "phonebook": {"Babatunde Fashola": "+234-803-212-293-4805",
                          "Sullivan Chime": "+234-803-212-452-2039"},
            "friends": [{"name": "Goodluck Jonathan",
                         "birth_date": "11/20/1957"},
                        {"name": "Ibrahim Badamasi Babangida",
                         "birth_date": "08/07/1941"}],
            "non_friends": ("Olusegun Obasanjo", "Sani Abacha"),
            "health": {"weight": 175, "vision": "20/20"}
        }
        self.assertDictEqual(expected,
                             convert_object_to_dict(self.test_person))

    def test_non_object_conversion(self):
        """Ensure that the same non-object element passed is returned."""
        self.assertEqual(100, convert_object_to_dict(100))
