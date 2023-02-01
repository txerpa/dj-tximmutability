# Changelog
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)


## [2.0.4]

### Added
* Tests with Python 3.11
### Fixed
* Django requirements
* isort version 5.10 cause an issue with pre-commit, updated to 5.12
* force_mutabililty flag in MutableQuerySet.update()
### Removed
* Drop support for Django < 3.2


## [2.0.0]

### Added
* Add support for Python 3.10
* Feature - add `MutabilityRule` attr `inst_conditions`.
* Feature - add `MutabilityRule` attr `inst_exclusion_conditions`.
* Feature - add `MutabilityRule` attr `queryset_conditions`.
* Feature - add `MutabilityRule` attr `queryset_exclusion_conditions`.
* Feature - add `MutabilityRule` attr `error_message` with string formatting.
* Feature - add `MutabilityRule` attr `error_code` to `ValidationError`.
* New exceptions `OrMutableException` and `RuleMutableException`.
* Feature mutability over `queryset.update(...)`.
* Implement Isort.
### Fixed
* Translations.
### Changed
* Test with [pytest](https://docs.pytest.org/).
### Removed
* Drop support for Python <= 3.7
* Drop support for Django < 2.1


## [1.0.0] - 2021-03-29

### Added
* Add support for Python 3.7, 3.8, 3.9
* Add support for Django 1.11, 2, 2.1, 2.2, 3.0, 3.1, 3.2
* Add dependency django-models-utils to implement ``FieldTracker``.
* Lint with **flake8** & **black**.
### Changed
* Rename nomenclature ``Immutability`` to ``Mutability``.
* Rename ``Rule`` class attributes.
* Delete ``update()`` method from ``MutableModel``. Mange this logic in ``save()``.
### Removed
* Drop support for Python <= 3.5
* Dropped usage of `django-rest-framework`.


## [0.1.0] - 2017-04-19

* First release.
