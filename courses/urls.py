# from django.urls import path
# from . import views

# app_name = "courses"

# urlpatterns = [

#     path(
#         "courses/<int:course_id>/students/",
#         views.instructor_course_students,
#         name="instructor_course_students",
#     ),

#     path(
#         "courses/<int:course_id>/students/<int:student_id>/chat/",
#         views.instructor_student_chat,
#         name="instructor_student_chat",
#     ),
#     path(
#         "student/courses/<int:course_id>/chat/",
#         views.student_instructor_chat,
#         name="student_instructor_chat",
#     ),


# ]
from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path(
        "courses/<int:course_id>/students/",
        views.instructor_course_students,
        name="instructor_course_students",
    ),
    path(
        "courses/<int:course_id>/students/<int:student_id>/chat/",
        views.instructor_student_chat,
        name="instructor_student_chat",
    ),
    path(
        "student/courses/<int:course_id>/chat/",
        views.student_instructor_chat,
        name="student_instructor_chat",
    ),
    path(
        "chat/<int:chat_id>/poll/",
        views.chat_poll,
        name="chat_poll",
    ),
    path(
        "chat/messages/<int:message_id>/react/",
        views.chat_react,
        name="chat_react",
    ),

    # Certificate download
    path(
        "student/certificate/<int:course_id>/download/",
        views.student_download_certificate,
        name="student_download_certificate",
    ),
]