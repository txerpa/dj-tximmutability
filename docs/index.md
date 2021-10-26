# Dj-Tximmutability Docs

Dj-Immutability is a small Django utils (Models Mixin, classes) that allows you to create mutability rules to make the model immutable with respect to the rules. It easy to use and combine with your models.

## Requirements
Dj-Tximmutability requires the following:

* Python (3.6, 3.7, 3.8, 3.9)
* Django (2.2, 3.0, 3.1, 3.2)

## Instalation
Install using pip.

```bash
pip install git+https://github.com/txerpa/dj-tximmutability.git@master#egg=dj-tximmutability
```
...or clone the project from github.
```bash
git clone https://github.com/encode/django-rest-framework
```
> **Pending to punblish on PyPI**


## Example

#### Customize your model code with MutabilityRule like this:

```python
from tximmutability.models import MutableModel

class Article(MutableModel):
    name = models.CharField(max_length=120)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    contents = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notas = models.TextField( blank=True, default='')
    ...
    
    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
            exclude_fields=('name', 'created', 'modified', 'contents', 'notas'),
            error_message=_("Message error - action %(action)s not allowed."),
        ),
    )
```
