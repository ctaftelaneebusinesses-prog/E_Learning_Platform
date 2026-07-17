from django.contrib.auth.models import User

from .models import Notification


def notify(user, message, link=''):
    Notification.objects.create(recipient=user, message=message, link=link)


def notify_all_students(message, link=''):
    students = User.objects.filter(profile__role='STUDENT')
    Notification.objects.bulk_create([
        Notification(recipient=student, message=message, link=link)
        for student in students
    ])


def notify_students_of_instructor(instructor, message, link=''):
    students = User.objects.filter(
        profile__role='STUDENT',
        enrollment__course__instructor=instructor
    ).distinct()
    Notification.objects.bulk_create([
        Notification(recipient=student, message=message, link=link)
        for student in students
    ])


def notify_course_students(course, message, link=''):
    students = User.objects.filter(
        profile__role='STUDENT',
        enrollment__course=course
    ).distinct()
    Notification.objects.bulk_create([
        Notification(recipient=student, message=message, link=link)
        for student in students
    ])
