from .views import get_current_employee


def auth_context(request):
    employee = get_current_employee(request)
    session_email = request.session.get("email")
    user_type = None
    if employee:
        user_type = "employee"
    elif session_email:
        from .models import User
        if User.objects.filter(email=session_email).exists():
            user_type = "user"
    return {
        "is_authenticated": bool(session_email),
        "user_type": user_type,
        "session_fullname": request.session.get("fullname"),
        "session_email": session_email,
    }
