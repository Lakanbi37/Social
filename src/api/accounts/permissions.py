from rest_framework.permissions import BasePermission
from apps.accounts.models import UserGroup, UserProfile


class GroupMemberPermission(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.has_perm("accounts.group_member"))


class IsGroupAdmin(BasePermission):
    MY_SAFE_METHODS = ["GET"]

    def has_permission(self, request, view):
        try:
            group = UserGroup.objects.get(admin=request.user)
        except Exception as e:
            return False
        if request.method in self.MY_SAFE_METHODS:
            return True
        return bool(request.user.has_perm("group_admin", group))


class IsUserProfile(BasePermission):
    MY_SAFE_METHODS = ['GET']

    def has_permission(self, request, view):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except Exception as e:
            return False
        if request.method in self.MY_SAFE_METHODS:
            return True
        return bool(request.user.has_perm("accounts.user_profile", profile))

    def has_object_permission(self, request, view, obj):
        if request.method in self.MY_SAFE_METHODS:
            return True
        return bool(request.user.has_perm("user_profile", obj))
