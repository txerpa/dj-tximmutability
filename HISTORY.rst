.. :changelog:

History
-------

Unreleased
----------

* Update setup.py
* Dropped support for Django 2.X.
* Rename nomenclature ``Immutability`` to ``Mutability``.
* Rename ``Rule`` class attributes.
* Delete ``update()`` method from ``MutableModel``. Mange this logic in ``save()``.
* Add dependency django-models-utils to implement ``FieldTracker``.

Version 0.1.0 (2017-04-19)
--------------------------

* First release on PyPI.
