from django.shortcuts import render

from courses.models import Course

def home(request):
    courses = Course.objects.filter(is_active=True)
    return render(request, 'home.html', {
        'courses': courses
    })

