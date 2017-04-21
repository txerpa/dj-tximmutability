=====
Usage
=====

To use Django Txerpa Immutability in a project, add it to your `INSTALLED_APPS`:

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
