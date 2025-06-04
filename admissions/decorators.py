from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def check_superadmin_and_roles(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        # Check if authenticated
        if not request.user.is_authenticated:
            return Response(
                {
                    "error": "Authentication required."
                }, 
                status=status.HTTP_401_UNAUTHORIZED)

        # Check if user is superuser
        if not request.user.is_superuser:
            return Response(
                {
                    "error": "Only super admins can perform this action."
                },
                status=status.HTTP_403_FORBIDDEN)

        return view_func(self, request, *args, **kwargs)

    return _wrapped_view


def consultant_only(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        # Check if authenticated
        if not request.user.is_authenticated:
            return Response(
                {
                    "error": "Authentication required."
                }, 
                status=status.HTTP_401_UNAUTHORIZED)

        # Check if user is superuser
        user_role = request.user.userprofile.role
        
        if user_role not in ["consultant", "admin"] :
            return Response(
                {
                    "error": "Only consultants can perform this action."
                },
                status=status.HTTP_403_FORBIDDEN)

        return view_func(self, request, *args, **kwargs)

    return _wrapped_view
