"""
django_param_validate - validate query parameters according to their
OpenAPI definitions.
"""

from drf_yasg import openapi
import re


class InvalidParameter(Exception):
    pass


def _validate_part(param, value):
    """
    Validate a parameter, or an item in a parameter.  Items can have the same
    validation requirements as parameters, possibly recursively, so we handle
    that possible recursion, as well as all validation, here.

    Validations we do:

    * Integers must be able to be converted into an integer.
    * Enums must have the value in the parameter's enum list.
    """
    if param.type != openapi.TYPE_STRING:
        if param.type == openapi.TYPE_INTEGER:
            try:
                param_value = int(param_value)
            except ValueError:
                raise InvalidParameter(
                    f"The value for the '{param.name}' field is required to be an integer"
                )
        if param.type == openapi.TYPE_BOOLEAN:
            # Booleans are very simple...
            return param_value in ('true', '1', 'yes')
        if param.type == openapi.TYPE_LIST:
            # Validate each part in turn and return a list with those values
            return [
                _validate_part(param.items, part)
                for part in ','.split(param_value)
            ]
        # Other type handling?

    # Check enumeration
    if hasattr(param, 'enum'):
        if param_value not in param.enum:
            raise InvalidParameter(
                f"The value for the '{param.name}' field is required to be one of"
                "the following values:" + ', '.join(str(e) for e in param.enum)
            )

    # Check pattern
    if hasattr(param, 'pattern'):
        regex = re.compile(param.pattern)
        if not re.fullmatch(param_value):
            raise InvalidParameter(
                f"The value '{param_value}' for parameter '{param.name}' did"
                f"not match the pattern {param.pattern}"
            )


def value_of_param(param, request):
    """
    Return the value of the given parameter in the request.

    If the parameter is not found in the request, this returns the
    parameter's default value, if it has one, or None.

    Validation of the parameter is also done.
    """
    if param.name not in request.query_params:
        if param.required:
            raise InvalidParameter(
                f"The {param.name} parameter was required but not supplied"
            )
        # Parameter not supplied, return the default or None
        return getattr(param, 'default', None)

    return _validate_part(param, request.query_params[param.name])
