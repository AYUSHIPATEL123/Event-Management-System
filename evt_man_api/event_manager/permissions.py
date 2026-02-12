from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, obj):
        return obj.user == request.user


class IsPublicEvent(BasePermission):
    def has_object_permission(self, request, obj):
        return obj.is_public and obj.user.is_authenticated 
