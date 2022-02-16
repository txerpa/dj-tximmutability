from django.core.exceptions import ValidationError


class OrMutableException(ValidationError):
    pass


class RuleMutableException(ValidationError):
    pass
