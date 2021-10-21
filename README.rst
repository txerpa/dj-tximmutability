=============================
Django Txerpa Immutability
=============================


[![codecov](https://codecov.io/gh/avallbona/Impostor/branch/master/graph/badge.svg)](https://codecov.io/gh/avallbona/Impostor)
[![Downloads](https://pepy.tech/badge/impostor)](https://pepy.tech/project/impostor)
[![Hit counter](http://hits.dwyl.com/avallbona/impostor.svg)](http://hits.dwyl.com/avallbona/impostor)
[![Python versions](https://img.shields.io/pypi/pyversions/impostor.svg)](https://pypi.org/project/Impostor/)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/impostor)
![Python package](https://github.com/avallbona/Impostor/workflows/Python%20package/badge.svg?branch=master)
![Upload Python Package](https://github.com/avallbona/Impostor/workflows/Upload%20Python%20Package/badge.svg?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/98d1f4b3225046e1aa839813b47bb44f)](https://www.codacy.com/manual/avallbona/Impostor?)

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
