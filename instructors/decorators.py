from django.shortcuts import redirect
from django.contrib import messages

def instructor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.profile.role != 'INSTRUCTOR':
            messages.error(request, "Instructor access only.")
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return wrapper
