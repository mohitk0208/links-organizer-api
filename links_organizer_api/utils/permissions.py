from rest_framework import permissions

from categories.models import AccessLevel


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user



class CategoryAccessPermission(permissions.IsAuthenticated):
    def __init__(
        self,
        read_level=AccessLevel.READ_ONLY,
        write_level=AccessLevel.READ_WRITE,
    ):
        super().__init__()
        self.read_level = read_level
        self.write_level = write_level

    def has_object_permission(self, request, _, obj):

        category = obj.get_category()

        if request.method in permissions.SAFE_METHODS:
            return True

        access = category.get_access_level(request.user.id)

        if access is None:
            return False

        return (
            access <= self.read_level
            if request.method in permissions.SAFE_METHODS
            else access <= self.write_level
        )
