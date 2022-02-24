# Dj-Tximmutability

---

[![Python package](https://github.com/txerpa/dj-tximmutability/actions/workflows/django.yml/badge.svg)](https://github.com/txerpa/dj-tximmutability/actions)
[![pre-commit](https://results.pre-commit.ci/badge/github/txerpa/dj-tximmutability/master.svg)](https://results.pre-commit.ci/latest/github/txerpa/dj-tximmutability/master)
[![codecov](https://codecov.io/gh/txerpa/dj-tximmutability/branch/master/graph/badge.svg)](https://codecov.io/gh/txerpa/dj-tximmutability/)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/txerpa/dj-tximmutability/blob/master/LICENSE)



Dj-Immutability is a Django application that allows you to create mutability rules to make the model immutable.

---
## [Contributing]( docs/CONTRIBUTING.md)
## [Changelog]( docs/CHANGELOG.md)

---

## Supports

* Python: (3.8, 3.9, 3.10)
* Django: (2.2, 3.0, 3.1, 3.2)


## Documentation

The full [documentation](https://bapons.github.io/dj-tximmutability/).


## Installation

```bash
pip install git+https://github.com/txerpa/dj-tximmutability.git@master#egg=dj-tximmutability
```

## Example

### Getting Started.

```python
from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule

class Article(MutableModel):
    name = models.CharField(max_length=120)
    contents = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notas = models.TextField( blank=True, default='')
    ...

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
        )
    )
```
