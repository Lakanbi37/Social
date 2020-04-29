from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.accounts.models import UserGroup
from apps.posts.models import Post


class OwnerPermission(BasePermission):
    message = 'You are not permitted to continue'
    my_safe_method = ['GET', 'PUT', 'DELETE']

    def has_permission(self, request, view):
        if request.method in self.my_safe_method:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False


class IsOwnerOrReadOnly(BasePermission):
    message = 'You must be the owner of this post.'
    my_safe_method = ['GET', 'PUT', 'DELETE']

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in self.my_safe_method:
                return True
            return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsGroupAdmin(BasePermission):
    message = "Insufficient Permission"

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("admin.is_admin", obj)


class IsGroupOrReadOnly(BasePermission):
    message = 'Permission denied'
    method = ['DELETE']

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in self.method:
                return True
            return False
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user in obj.members.all()
