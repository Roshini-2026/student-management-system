from django.contrib.auth.decorators import login_required, permission_required


def permission_needed(perm):
    """Logged-out users go to the login page. Logged-in users without the permission get a 403."""
    def decorator(view):
        return login_required(permission_required(perm, raise_exception=True)(view))
    return decorator 