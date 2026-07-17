from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.role == 'ADMIN':
            return view_func(request, *args, **kwargs)
        messages.error(request, "Admin access only")
        return redirect('login')
    return wrapper
