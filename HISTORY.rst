.. :changelog:

History
-------

0.3.3 (2016-05-15)
~~~~~~~~~~~~~~~~~~~~~

* Fixed bug where global LUT would leak data when calling expressions
  within custom lookups. See `#11 <https://github.com/dealertrack/simplepath/issues/11>`_.
* Switched to using Python 3.5 vs 3.4 for running Travis builds.

0.3.2 (2015-09-14)
~~~~~~~~~~~~~~~~~~~~~

* Registered ``AsTypeLookup`` and ``ArithmeticLookup`` as ``as_type`` and ``arith`` lookups
  in default lookup registry

0.3.1 (2015-08-28)
~~~~~~~~~~~~~~~~~~~~~

* Added the ``AsTypeLookup`` and ``ArithmeticLookup``

0.3.0 (2015-07-15)
~~~~~~~~~~~~~~~~~~~~~

* Added ability to use lists in the simplepath config which will generate a list in the mapped data

0.2.0 (2015-06-26)
~~~~~~~~~~~~~~~~~~~~~

* Added ``deepvars`` utility which is useful when using simplepath with objects

0.1.1 (2015-03-31)
~~~~~~~~~~~~~~~~~~~~~

* Fixed a link to the repo in the package description

0.1.0 (2015-01-08)
~~~~~~~~~~~~~~~~~~~~~

* First release
