=============================
Django Txerpa Immutability
=============================

.. image:: https://badge.fury.io/py/dj-tximmutability.svg
    :target: https://badge.fury.io/py/dj-tximmutability

.. image:: https://travis-ci.org/marija_milicevic/dj-tximmutability.svg?branch=master
    :target: https://travis-ci.org/marija_milicevic/dj-tximmutability

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://codecov.io/gh/marija_milicevic/dj-tximmutability/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/marija_milicevic/dj-tximmutability


Your project description goes here

Documentation
-------------

The full documentation is at https://dj-tximmutability.readthedocs.io.

Quickstart
----------

Install Django Txerpa Immutability::

    pip install dj-tximmutability

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'tximmutability.apps.TximmutabilityConfig',
        ...
    )

Add Django Txerpa Immutability's URL patterns:

.. code-block:: python

    from tximmutability import urls as tximmutability_urls


    urlpatterns = [
        ...
        url(r'^', include(tximmutability_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
