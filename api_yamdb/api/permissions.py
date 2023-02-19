from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAdminOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_admin
                or request.user.is_superuser)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_admin
                or request.method in SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated
                or request.method in SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return (obj.author == request.user
                    or (request.user.is_authenticated
                        and request.user.is_admin
                        or request.user.is_moderator
                        or request.user.is_superuser)
                    )
        return (request.method in SAFE_METHODS or obj.author == request.user
                or (request.user.is_authenticated and request.user.is_admin)
                )


class IsAdminModeratorOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or (request.user.is_authenticated and request.user.is_admin)
                )
