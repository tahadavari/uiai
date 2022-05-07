from rest_framework.permissions import BasePermission

from blog.models import Post


class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)


class IsWriter(BasePermission):
    def has_permission(self, request, view, post_hash):
        user = Post.objects.hash(post_hash).author
        return bool(request.user == user)

