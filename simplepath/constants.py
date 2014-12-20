from __future__ import unicode_literals


# special None singleton which can be used
# to differentiate whether a value is not provided,
# provided or provided as None
NONE = type(str('None'), (object,), {'__init__': lambda self: None()})


class FailMode(object):
    FAIL_IF_REQUIRED = 'fail_if_required'
    FAIL = 'fail'
    SKIP = 'skip'
