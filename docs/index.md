# Dj-Tximmutability

---

Dj-Immutability is a small Django utils (Models Mixin, classes) that allows you to create mutability rules to make the model immutable.


### [CONTRIBUTING]( ./CONTRIBUTING.md)
### [CHANGELOG]( ./CHANGELOG.md)

## Requirements
Dj-Tximmutability requires the following:

* Python: (3.8, 3.9, 3.10)
* [Django](https://github.com/django/django): (2.2, 3.0, 3.1, 3.2)
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

## Rule options.


### field_rule *
Model field name.

* **Required**
* **Type**: String

---
### values *
Tuple of values of `field_rule` by which it can be mutable.

* **Required**
* **Tuple** - at least one element.

---
### exclude_fields
Tuple of fields to be ignored.

* **Optional**
* **Type**: Tuple
* **Default**: ()

#### Example

```python
...
from django.utils.translation import gettext_lazy
from django.db import models

from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule


class Article(MutableModel):
    name = models.CharField(max_length=120)
    content = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notes = models.TextField( blank=True, default='')
    ...

    def no_notes(self):
        return self.notes == ''

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
            exclude_fields=('notes',)
        ),
    )
```

Code that executes the above rule.
```python
queryset = Article.objects.all()
queryset.update(name="-")
...
instance = Article.objects.first()
instance.name = "-"
instance.save()
```

Code that does not execute the above rule.
```python
queryset = Article.objects.all()
queryset.update(name="-")  # excluded field
queryset.update(state="-")  # is the field in which the rule is managed.
...
instance = Article.objects.first()
instance.notes = "-"
instance.save() # excluded field
```

---
### exclude_on_create
Exclude rule on create.

* **Optional**
* **Type**: Boolean
* **Default**: `True`

---
### exclude_on_update
Exclude rule on update instance or queryset.

* **Optional**
* **Type**: Boolean
* **Default**: `False`

---
### exclude_on_delete
Exclude rule on delete instance.

* **Optional**
* **Type**: Boolean
* **Default**: `False`

---
### inst_conditions
This attribute, effects when the action comes from an instance,
is not checked for a queryset.
It is a tuple of conditional methods that return Boolean.
All conditions must be met to run the rule.
If one condition not met, the rule would not be executed,
and therefore the instance would continue with the action.

* **Optional**
* **Type**: Tuple
* **Default**: ()

#### Example

```python
...
from django.utils.translation import gettext_lazy
from django.db import models

from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule


class Article(MutableModel):
    name = models.CharField(max_length=120)
    content = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notes = models.TextField( blank=True, default='')
    ...

    def no_notes(self):
        return self.notes == ''

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
            inst_conditions=(no_notes,)
        ),
    )
```

Code that executes the above rule.
```python
# Attribute `inst_conditions` has no effect over queryset. Rule will be executed.
queryset = Article.objects.exclude(notes="")
queryset.update(name="-")
...
# Codition met - continue executing Rule
instance = Article.objects.filter(notes="").first()
instance.name = "-"
instance.save()
```

Code that does not execute the above rule.
```python
# Changes on `state` field has no efect, is the field on which the rule is managed.
instance = Article.objects.filter(notes="").first()
instance.state = "draft"  # `state` field is excluded
instance.save()
...
# Condition of `inst_conditions` not met, rule is excluded.
instance = Article.objects.exclude(notes="")
instance.name = "-"
instance.save()
```

---
### inst_exclusion_conditions
This attribute, effects when the action comes from an **instance**,
is not checked for a **queryset**.
It is a tuple of conditional methods that return Boolean.
No conditions must be met to execute the rule.
If a condition is met, the rule will not be executed
and thus the instance would continue with the action.

Opossite of `inst_conditions`.

* **Optional**
* **Type**: Tuple
* **Default**: ()

#### Example

```python
...
from django.utils.translation import gettext_lazy
from django.db import models

from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule


class Article(MutableModel):
    name = models.CharField(max_length=120)
    content = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notes = models.TextField( blank=True, default='')
    ...

    def no_notes(self):
        return self.notes == ''

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
            inst_exclusion_conditions=(no_notes,)
        ),
    )
```

Code that executes the above rule.
```python
# Attribute `inst_exclusion_conditions` has no effect over queryset. Rule will be executed.
queryset = Article.objects.filter(notes="")
queryset.update(name="-")
...
# No codition met - continue executing Rule
instance = Article.objects.exclude(notes="").first()
instance.name = "-"
instance.save()
```

Code that does not execute the above rule.
```python
# Changes on `state` field has no efect, is the field on which the rule is managed.
instance = Article.objects.exclude(notes="").first()
instance.state="draft"
instance.save()
...
# Condition of `inst_exclusion_conditions` met, rule is excluded.
instance = Article.objects.filter(notes="").first()
instance.name = "-"
instance.save()
```

---
### queryset_conditions
This attribute, effects when the action comes from a Queryset,
is not checked for a single instance.
It is a tuple of conditional methods that return Boolean.
Those methods must come from the model manager.
All conditions must be met to run the rule.
If one condition not met, the rule would not be executed,
and therefore the instance would continue with the action.

Similar to `inst_conditions`, but for queryset.

* **Optional**
* **Type**: Tuple
* **Default**: ()

#### Example

```python
...
from django.utils.translation import gettext_lazy
from django.db import models

from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule
from tximmutability.models import MutableQuerySet

class ArticleQuerySet(MutableQuerySet, models.QuerySet):

    def no_notes(self):
        return self.count() == self.filter(notes='').count()

class Article(MutableModel):
    name = models.CharField(max_length=120)
    content = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notes = models.TextField( blank=True, default='')
    objects = ArticleQuerySet.as_manager()
    ...

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
            queryset_conditions=(object.no_notes,)
        ),
    )
```

Code that executes the above rule.
```python
# Codition met - continue executing Rule
queryset = Article.objects.filter(notes="")
queryset.update(name="-")
...
# Attribute `queryset_conditions` has no effect over single instance. Rule will be executed.
instance = Article.objects.exclude(notes="").first()
instance.name = "-"
instance.save()
```

Code that does not execute the above rule.
```python
# Changes on `state` field has no efect, is the field on which the rule is managed.
queryset_0 = Article.objects.filter(notes="")
queryset_0.update(state="draft")
...
# Condition of `queryset_conditions` not met, rule is excluded.
queryset_1 = Article.objects.exclude(notes="")
queryset_1.update(name="-")  # `queryset_conditions` not met
```

---
### queryset_exclusion_conditions
This attribute, effects when the action comes from a Queryset,
is not checked for a single instance.
It is a tuple of conditional methods that return Boolean.
Those methods must come from the model manager.
No conditions must be met to execute the rule.
If one condition is met, the rule would not be executed,
and therefore the instance would continue with the action.

Similar to `inst_exclusion_conditions`, but for queryset.

* **Optional**
* **Type**: Tuple
* **Default**: ()

#### Example

```python
...
from django.utils.translation import gettext_lazy
from django.db import models

from tximmutability.models import MutableModel
from tximmutability.rule import MutabilityRule
from tximmutability.models import MutableQuerySet

class ArticleQuerySet(MutableQuerySet, models.QuerySet):

    def no_notes(self):
        return self.count() == self.filter(notes='').count()

class Article(MutableModel):
    name = models.CharField(max_length=120)
    content = models.TextField()
    state = models.ChoiceField(choices=['draft', 'published'])
    notes = models.TextField( blank=True, default='')
    objects = ArticleQuerySet.as_manager()
    ...

    mutability_rules = (
        MutabilityRule(
            'state',
            values=('draft',),
            queryset_exclusion_conditions=(object.no_notes,)
        ),
    )
```

Code that executes the above rule.
```python
# Codition not met - continue executing Rule
queryset = Article.objects.exclude(notes="")
queryset.update(name="-")  # state is excluded
...
# Attribute `queryset_exclusion_conditions` has no effect over single instance. Rule will be executed.
instance = Article.objects.filter(notes="").first()
instance.name = "-"
instance.save()  # For a single instance `queryset_exclusion_conditions` has no effect.
```

Code that does not execute the above rule.
```python
# Changes on `state` field has no efect, is the field on which the rule is managed.
queryset_0 = Article.objects.exclude(notes="")
queryset_0.update(state="draft")
...
# Condition of `queryset_exclusion_conditions` met, rule is excluded.
queryset_1 = Article.objects.filter(notes="")
queryset_1.update(name="-")
```

---
### error_message
Expect a **String**.
It accepts custom [string formatting](https://docs.python.org/3/library/string.html#string-formatting)
by variable substitutions. Accepted variables `[{action} {field_rule} {values}]`.

* **Optional**
* **Type**: String
* **Default**: None


#### Example
```python
...
from django.utils.translation import gettext_lazy

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
            error_message=gettext_lazy("Article can not be {action}, {field_rule} is not \"{values}\"")
        ),
    )
```

---
### error_code
If the Rule fails it return `RuleMutableException` or `OrMutableException`, both inherit from ValidationError.
This has an attribute (code), where it can be handled later on the catch error.
Therefore, `error_code` provides the ability to pass the value to both exceptions.

* **Optional**
* **Type**: String
* **Default**: None

#### Example
```python
...
from django.utils.translation import gettext_lazy

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
            error_code="0001"
        ),
    )
```
...
```python
# Example how can be handled depending on our purpose
try:
    instance.save()
except RuleMutableException as exc:
    if exc.code == "0001":
        # Do whaterever, send email, execute task, etc.
```
---
## Exclude rules.
In some cases, you will need to ignore the model rules.

```python
instance.save(force_mutability=True, ...)

```
```python
instance.delete(force_mutability=True, ...)
```
---

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
