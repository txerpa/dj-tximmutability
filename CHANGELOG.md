.. :changelog:

# Changelog

## 2.0.0 (2022-02-04)

* Drop support for Python <= 3.7
* Add support for Python 3.10
* Drop support for Django <= 2.2
* Feature - add ``Rule`` attr ``conditions``.
* Feature - add ``Rule`` attr ``exclusion_conditions``.
* Feature - add ``Rule`` attr ``error_code`` to ``ValidationError``.
* Feature dependency django-models-utils to implement ``FieldTracker``.
* Test with **pytest**.


## 1.0.0 (2021-03-29)

* Drop support for Python <= 3.5
* Add support for Python 3.7, 3.8, 3.9
* Add support for Django 1.11, 2, 2.1, 2.2, 3.0, 3.1, 3.2
* Dropped usage of `django-rest-framework`
* Rename nomenclature ``Immutability`` to ``Mutability``.
* Rename ``Rule`` class attributes.
* Delete ``update()`` method from ``MutableModel``. Mange this logic in ``save()``.
* Add dependency django-models-utils to implement ``FieldTracker``.
* Lint with **flake8** & **black**.
* Add github actions.


## 0.1.0 (2017-04-19)

* First release.
