# Dj-Tximmutability

Dj-Immutability is a small Django utils (Models Mixin, classes) that allows you to create mutability rules to make the model immutable.

## Requirements
Dj-Tximmutability requires the following:

* Python: (3.8, 3.9, 3.10)
* Django: (2.2, 3.0, 3.1, 3.2)

Others:
* [Django](https://github.com/django/django) >=2.2 - <=3.2
* [django-model-utils](https://github.com/jazzband/django-model-utils) == 4.1.1

## Instalation
Install using pip.

```bash
pip install git+https://github.com/txerpa/dj-tximmutability.git@master#egg=dj-tximmutability
```
...or clone the project from github.
```bash
git clone https://github.com/txerpa/dj-tximmutability
```
> **Pending to punblish on PyPI**


## Example

### Minimal implementation.
Create a `MutabilityRule` over the` state` field when it is ** draft **.
This means that this model is mutable only when `state == 'draft'`.

```python
from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule

class Article(MutableModel):
    name = models.CharField(max_length=120)
    content = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notes = models.TextField( blank=True, default='')
    ...

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',)
        )
    )
```

### Exclude fields.

In some cases, it is necessary to exclude some fields from `MutabilityRule`.
This means that this model is mutable only when `state == 'draft'`, but if you modify only the excluded fields,
the instance would be mutable for those fields.
```python
...
from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule

class Article(MutableModel):
    name = models.CharField(max_length=120)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    content = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notes = models.TextField( blank=True, default='')
    ...

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
            exclude_fields=('created', 'modified')
        ),
    )
```

### Custom error message.

`MutabilityRule` can return a custom message error, adding `error_message` kwargs.
```python
...
from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule

class Article(MutableModel):
    name = models.CharField(max_length=120)
    content = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notes = models.TextField( blank=True, default='')
    ...

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
            error_message=_("Article can not be mutated, state is not \"borrador\"")
        ),
    )
```

## Running Tests

Does the code actually work?

* Install all the python interpreters you need via [pyenv](https://github.com/pyenv/pyenv). E.g.:
```bash
pyenv install 3.10.2
pyenv install 3.9.2
pyenv install 3.8.8
```

* Make them global with:
```bash
pyenv global 3.9.2 3.8.8 3.10.2
```

* Run tests
```bash
workon <YOURVIRTUALENV>
(myenv) $ pip install -r requirements/requirements_dev.txt
```
```bash
(myenv) $ tox
```
or
```bash
(myenv) $ pytest tests
```

### [CONTRIBUTING]( ../CONTRIBUTING.md)
### [CHANGELOG]( ../CHANGELOG.md)


<!--
##Features

TODO

-->
