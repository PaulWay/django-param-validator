"""
django_param_validate - validate query parameters according to their
OpenAPI definitions.
"""

from datetime import datetime
from django.utils.dateparse import parse_date, parse_datetime
from django.utils timezone import make_aware
from drf_yasg import openapi
import re


class InvalidParameterDefinition(Exception):
    pass


def _validate_part(name, param, value):
    """
    Validate a parameter, or an item in a parameter.  Items can have the same
    validation requirements as parameters, possibly recursively, so we handle
    that possible recursion, as well as all validation, here.

    Validations we do:

    * Integers must be able to be converted into an integer.
    * Enums must have the value in the parameter's enum list.
    """
    # Parse arrays by splitting them and recursively validating the values.
    if param.type == openapi.TYPE_ARRAY:
        # Split value into parts and recursively validate them
        collection_format = getattr(param, 'collectionFormat', None)
        if not collection_format:
            raise InvalidParameterDefinition(
                "Array parameter collection format not defined"
            )
        splitter_for = {'csv': ',', 'ssv': ' ', 'tsv': '\t', 'pipes': '|'}
        values = []
        if collection_format in splitter_for:
            values = value.split(splitter_for[collection_format])
        elif collection_format == 'multi':
            # No idea if Django handles multiple arguments by putting them
            # into an array itself, but let's start with this idea
            values = value
        else:
            raise InvalidParameterDefinition(
                f"Array parameter collection format {collection_format} not recognised"
            )
        if param.items_ is None:
            raise InvalidParameterDefinition(
                "Array parameter has not defined the type of its items"
            )
        return [validate_param_part(name, param.items_, v) for v in values]

    # Handle any Pythonic type conversions first
    if param.type == openapi.TYPE_BOOLEAN:
        # Booleans don't do any further processing, so exit now
        return value in ('true', '1', 'yes')

    elif param.type == openapi.TYPE_INTEGER:
        try:
            value = int(value)
        except ValueError:
            raise ValueError(
                f"The value for the '{name}' field must be an integer"
            )
    elif param.type == openapi.TYPE_NUMBER:
        try:
            value = float(value)
        except ValueError:
            raise ValueError(
                f"The value for the '{name}' field must be a floating point number"
            )
    elif param.type == openapi.TYPE_STRING:
        # Check string pattern and format possibilities.
        pattern = getattr(param, 'pattern', None)
        if pattern:
            if not re.match(pattern, value):
                raise BadRequest(
                    f"The value of the '{name}' field did not match the "
                    f"pattern '{pattern}'"
                )
        param_format = getattr(param, 'format', 'NONE')
        if param_format == openapi.FORMAT_DATE:
            try:
                # datetime.date objects cannot be timezone aware, so they
                # have to be converted into datetimes.  Haven't found a better
                # way of doing this:
                value = make_aware(datetime.fromordinal(parse_date(value).toordinal()))
            except ValueError:
                raise BadRequest(
                    f"The value for the '{name}' field did not look like a date"
                )
        elif param_format == openapi.FORMAT_DATETIME:
            try:
                value = make_aware(parse_datetime(value))
            except ValueError:
                raise BadRequest(
                    f"The value for the '{name}' field did not look like a datetime"
                )
        # We don't check any of the other formats here (yet).

    # Check enumeration
    if hasattr(param, 'enum'):
        if value not in param.enum:
            raise ValueError(
                f"The value for the '{name}' field is required to be one of"
                "the following values:" + ', '.join(str(e) for e in param.enum)
            )

    # Check pattern
    if hasattr(param, 'pattern'):
        regex = re.compile(param.pattern)
        if not re.fullmatch(value):
            raise ValueError(
                f"The value '{value}' for parameter '{name}' did"
                f"not match the pattern {param.pattern}"
            )

    # OK, validation has passed, return the value here
    return value


def value_of_param(param, request):
    """
    Return the value of the given parameter in the request.

    If the parameter is not found in the request, this returns the
    parameter's default value, if it has one, or None.

    Validation of the parameter is also done.
    """
    if param.in_ == openapi.IN_BODY:
    if param.in_ == openapi.IN_PATH:
    if param.in_ == openapi.IN_QUERY:
        if param.name not in request.query_params:
            return None
        value = request.query_params[param.name]
    if param.in_ == openapi.IN_FORM:
    if param.in_ == openapi.IN_HEADER:
        if param.name not in request.META:
            return None
        value = request.META[param.name]

    return _validate_part(param.name, param, value)
