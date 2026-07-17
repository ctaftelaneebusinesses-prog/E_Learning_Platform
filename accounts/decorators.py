from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.role == 'STUDENT':
            return view_func(request, *args, **kwargs)

        messages.error(request, "Student access only")
        return redirect('login')   # ✅ safe fallback
    return wrapper


def instructor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.role == 'INSTRUCTOR':
            return view_func(request, *args, **kwargs)

        messages.error(request, "Instructor access only")
        return redirect('login')   # ✅ safe fallback
    return wrapper
