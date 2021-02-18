# django-param-validator
Validate parameter inputs against an OpenAPI parameter specification

# Usage

```
from drf_yasg import openapi
from django_param_validator import value_of_param

my_query_param = openapi.PARAMETER(
    name='parrot_status', in_=openapi.QUERY,
    type=openapi.STRING,
)

def django_view(self, request):
    status = value_of_param(my_query_param, request)
    return Response("Your parrot is: " + status)
```
