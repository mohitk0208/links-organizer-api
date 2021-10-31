from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.fields import get_error_detail
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):

    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(detail={"detail": get_error_detail(exc)[0]})

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    # response = drf_exception_handler(exc, context)
    # if response is not None:
    #     response.data = {
    #         "message": response.data.get("detail", "Unexpected error occured.")
    #     }
    # return response
    return drf_exception_handler(exc, context)
