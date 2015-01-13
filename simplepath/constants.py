# -*- coding: utf-8 -*-
from __future__ import unicode_literals


DELIMITERS = {
    'lookup': {
        'start': '<',
        'end': '>',
    },
    'expression': '.',
}

# special None singleton which can be used
# to differentiate whether a value is not provided,
# provided or provided as None
NONE = type(str('None'), (object,), {'__init__': lambda self: None()})


class FailMode(object):
    DEFAULT = 'default'
    FAIL = 'fail'
    SKIP = 'skip'

    @classmethod
    def is_valid(cls, fail_mode):
        return fail_mode in vars(cls).values()

DEFAULT_FAIL_MODE = FailMode.FAIL
