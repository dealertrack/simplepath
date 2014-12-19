from __future__ import unicode_literals


NONE = type(str('None'), (object,), {'__init__': lambda self: None()})
