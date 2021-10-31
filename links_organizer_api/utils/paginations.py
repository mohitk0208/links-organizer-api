from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    A custom pagination class
    """

    default_limit = 10
    max_limit = 30
