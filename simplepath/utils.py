# -*- coding: utf-8 -*-
"""Module that describes all utility functions for Simplepath."""
from __future__ import unicode_literals


def deepvars(data_object):
    """
    Recursively convert all of the object attributes into a dictionary.

    Example:

    ::

        >>> class Planet(object):
        ...    def __init__(self, name, residents):
        ...        self.name = name
        ...        self.residents = residents
        >>> assert deepvars(Planet("Mars", "martians")) == {
        ...     "name": "Mars",
        ...     "residents": "martians",
        ... }

    Args:
        data_object (object): any Python object

    Returns:
        The dictionary representation of all fields in the Python object.
    """

    if hasattr(data_object, '__slots__') or hasattr(data_object, '__dict__'):
        if hasattr(data_object, '__slots__'):
            object_dict = {attr: getattr(data_object, attr)
                           for attr in data_object.__slots__}
        else:
            object_dict = vars(data_object).copy()
        for attrib_name, attrib_val in object_dict.items():
            if isinstance(attrib_val, (tuple, list)):
                object_dict[attrib_name] = [deepvars(element)
                                            for element in attrib_val]
            elif isinstance(attrib_val, dict):
                object_dict[attrib_name] = {
                    key: deepvars(attrib_val[key])
                    for key in attrib_val
                }
            else:
                # This case assumes that attrib_val is a
                # non-iterable object.
                object_dict[attrib_name] = deepvars(attrib_val)

        return object_dict
    else:
        return data_object
