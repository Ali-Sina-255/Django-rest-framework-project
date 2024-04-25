from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions


class IsAdminOrReadyOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class FullDjangoModelPermission(DjangoModelPermissions):
    def __init__(self) -> None:
        super().__init__()
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s'],


class ViewCustomerHistoryPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("store.view_history")
