# Dj-Tximmutability

---

[![Python package](https://github.com/bapons/dj-tximmutability/actions/workflows/django.yml/badge.svg)](https://github.com/bapons/dj-tximmutability/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/bapons/dj-tximmutability/master.svg)](https://results.pre-commit.ci/latest/github/bapons/dj-tximmutability/master)
[![codecov](https://codecov.io/gh/bapons/dj-tximmutability/branch/master/graph/badge.svg)](https://codecov.io/gh/bapons/dj-tximmutability/)


<!--[![pypi](https://img.shields.io/pypi/v/dj-tximmutability.svg)](https://pypi.python.org/pypi/dj-tximmutability/)-->
<!--[![Python versions](https://img.shields.io/pypi/pyversions/dj-tximmutability.svg)](https://pypi.org/project/dj-tximmutability/)-->
<!--![PyPI - Django Version](https://img.shields.io/pypi/djversions/dj-tximmutability)-->
<!--[![Python versions](https://img.shields.io/pypi/status/dj-tximmutability.svg)](https://img.shields.io/pypi/status/dj-tximmutability.svg/)-->
<!--[![Python versions](https://codecov.io/gh/marija_milicevic/dj-tximmutability/branch/master/graph/badge.svg)](https://codecov.io/gh/marija_milicevic/dj-tximmutability)-->

Dj-Immutability is a Django application that allows you to create mutability rules to make the model immutable.

## Supports 

* Python: (3.6, 3.7, 3.8, 3.9)  
* Django: (1.8, 1.9, 1.10, 1.11, 2.1, 2.2, 3.0, 3.1, 3.2)


## Documentation

The full documentation is at https://bapons.github.io/dj-tximmutability/.


## Installation
 
```bash
pip install git+https://github.com/txerpa/dj-tximmutability.git@master#egg=dj-tximmutability
```

## Example

### Minimal implementation.

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

## [Contributing](./CONTRIBUTING.md)
