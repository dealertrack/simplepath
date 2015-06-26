==========
simplepath
==========

.. image:: https://badge.fury.io/py/simplepath.png
    :target: http://badge.fury.io/py/simplepath

.. image:: https://travis-ci.org/dealertrack/simplepath.png?branch=master
    :target: https://travis-ci.org/dealertrack/simplepath

.. image:: https://coveralls.io/repos/dealertrack/simplepath/badge.svg
    :target: https://coveralls.io/r/dealertrack/simplepath


``simplepath`` is a library for data-structure lookups
using super simple expressions with performance in mind.
*"simplepath"* is a word play on some other ``*path`` technologies
such as ``xpath``, ``jsonpath``, ``jpath``, etc.

* Free software: MIT license
* GitHub: https://github.com/dealertrack/simplepath

Inspiration
-----------

The inspiration for ``simplepath`` was performance. Many other
libraries focus on making single lookups, however they fall 
short when a lot of data needs to be queried.

For example if a dictionary with some structure needs to be converted
into another dictionary with a different structure, a simple and
configurable way of doing that might be to define a configuration
dictionary where the keys will be the keys of the output dictionary, 
and values will be lookup expressions to get appropriate data::

    {
        "greetings": "foo.greeting",
        "planet": "foo.[0].planet",
        ...
    }

The above approach is easy to implement, however is not very performant
since for each lookup the lookup expression will have to be evaluated.
At dealertrack, we needed to do something similar at some point and
tried `jsonpath-rw <https://pypi.python.org/pypi/jsonpath-rw>`_
which would sometimes take 15 seconds to map dictionaries with only
a couple hundred expressions. Upon some investigation, most of the
time was being spent in `ply <https://pypi.python.org/pypi/ply>`_.
Unfortunately we did not find another comparable library which
accomplished everything we needed, and satisfied our performance
requirements, so ``simplepath`` was born.

Installing
----------

You can install ``simplepath`` using pip::

    $ pip install simplepath

Quick Guide
-----------

Here is a quick example.

::

    from simplepath.mapper import Mapper

    class MyMapper(Mapper):
        config = {
            'greetings': 'example.greetings',
            'to': 'example.planets.<find:planet=Earth>.residents',
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
        }
    }

    MyMapper.map_data(data) == {
        'greetings': 'Hello',
        'to': 'people',
    }

Testing
-------

To run the tests you need to install testing requirements first::

    $ make install

Then to run tests, you can use ``nosetests`` or simply use Makefile command::

    $ nosetests -sv
    # or
    $ make test
