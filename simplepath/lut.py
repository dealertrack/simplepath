# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class LUT(dict):
    def __init__(self, *args, **kwargs):
        super(LUT, self).__init__(*args, **kwargs)
        self.reads = 0
        self.writes = 0

    def __getitem__(self, *args, **kwargs):
        self.reads += 1
        return super(LUT, self).__getitem__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        self.writes += 1
        return super(LUT, self).__setitem__(*args, **kwargs)
