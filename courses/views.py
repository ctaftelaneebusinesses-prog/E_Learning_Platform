# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User

# from accounts.decorators import instructor_required
# from .models import (
#     Course,
#     Enrollment,
#     InstructorStudentChat,
#     InstructorStudentMessage
# )


# @login_required
# @instructor_required
# def instructor_course_students(request, course_id):
#     course = get_object_or_404(
#         Course,
#         id=course_id,
#         instructor=request.user
#     )

#     enrollments = (
#         Enrollment.objects
#         .filter(course=course)
#         .select_related("student")
#     )

#     return render(
#         request,
#         "instructors/course_students.html",
#         {
#             "course": course,
#             "enrollments": enrollments,
#             "student_count": enrollments.count(),
#         }
#     )


# @login_required
# @instructor_required
# def instructor_student_chat(request, course_id, student_id):
#     course = get_object_or_404(
#         Course,
#         id=course_id,
#         instructor=request.user
#     )

#     student = get_object_or_404(User, id=student_id)

#     # 🔐 Ensure student is enrolled in this course
#     get_object_or_404(
#         Enrollment,
#         course=course,
#         student=student
#     )

#     chat, _ = InstructorStudentChat.objects.get_or_create(
#         course=course,
#         instructor=request.user,
#         student=student
#     )

#     if request.method == "POST":
#         message = request.POST.get("message", "").strip()
#         if message:
#             InstructorStudentMessage.objects.create(
#                 chat=chat,
#                 sender=request.user,
#                 message=message
#             )
#         return redirect(
#             "courses:instructor_student_chat",
#             course_id=course.id,
#             student_id=student.id
#         )

#     messages = chat.messages.all()

#     return render(
#         request,
#         "chat/instructor_student_chat.html",
#         {
#             "course": course,
#             "student": student,
#             "messages": messages,
#         }
#     )

# @login_required
# def student_instructor_chat(request, course_id):
#     course = get_object_or_404(Course, id=course_id)

#     enrollment = get_object_or_404(
#         Enrollment,
#         course=course,
#         student=request.user
#     )

#     chat, _ = InstructorStudentChat.objects.get_or_create(
#         course=course,
#         instructor=course.instructor,
#         student=request.user
#     )

#     if request.method == "POST":
#         InstructorStudentMessage.objects.create(
#             chat=chat,
#             sender=request.user,
#             message=request.POST.get("message")
#         )
#         return redirect(
#             "courses:student_instructor_chat",
#             course_id=course.id
#         )

#     messages = chat.messages.all()

#     return render(
#         request,
#         "students/student_instructor_chat.html",
#         {
#             "course": course,
#             "messages": messages,
#             "instructor": course.instructor
#         }
#     )
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods

from django.urls import reverse

from accounts.decorators import instructor_required
from accounts.notifications import notify
from .chat_utils import is_online, mark_read, serialize_message, tick_state
from .models import (
    Course,
    Enrollment,
    InstructorStudentChat,
    InstructorStudentMessage,
    MessageReaction,
    Certificate,
)

REACTION_EMOJIS = ['👍', '❤️', '😂', '😮', '😢', '🙏']


@login_required
@instructor_required
def instructor_course_students(request, course_id):
    course = get_object_or_404(
        Course,
        id=course_id,
        instructor=request.user
    )

    enrollments = (
        Enrollment.objects
        .filter(course=course)
        .select_related("student")
    )

    return render(
        request,
        "instructors/course_students.html",
        {
            "course": course,
            "enrollments": enrollments,
            "student_count": enrollments.count(),
        }
    )


@login_required
@instructor_required
def instructor_student_chat(request, course_id, student_id):
    course = get_object_or_404(
        Course,
        id=course_id,
        instructor=request.user
    )

    student = get_object_or_404(User, id=student_id)

    get_object_or_404(
        Enrollment,
        course=course,
        student=student
    )

    chat, _ = InstructorStudentChat.objects.get_or_create(
        course=course,
        instructor=request.user,
        student=student
    )

    if request.method == "POST":
        return _handle_chat_post(request, chat, notify_recipient=student,
                                  redirect_url=reverse("courses:instructor_student_chat",
                                                        args=[course.id, student.id]),
                                  recipient_link=reverse("courses:student_instructor_chat", args=[course.id]))

    mark_read(chat, request.user)
    other_online = is_online(student)

    return render(
        request,
        "chat/instructor_student_chat.html",
        {
            "course": course,
            "student": student,
            "chat": chat,
            "other_online": other_online,
            "messages": [serialize_message(m, request.user, other_online) for m in chat.messages.all()],
            "reaction_emojis": REACTION_EMOJIS,
            "reaction_emojis_json": json.dumps(REACTION_EMOJIS),
            "poll_url": reverse("courses:chat_poll", args=[chat.id]),
            "react_url_template": reverse("courses:chat_react", args=[999999999]),
        }
    )


@login_required
def student_instructor_chat(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    get_object_or_404(
        Enrollment,
        course=course,
        student=request.user
    )

    chat, _ = InstructorStudentChat.objects.get_or_create(
        course=course,
        instructor=course.instructor,
        student=request.user
    )

    if request.method == "POST":
        recipient_link = (
            reverse("courses:instructor_student_chat", args=[course.id, request.user.id])
            if course.instructor else ''
        )
        return _handle_chat_post(request, chat, notify_recipient=course.instructor,
                                  redirect_url=reverse("courses:student_instructor_chat", args=[course.id]),
                                  recipient_link=recipient_link)

    mark_read(chat, request.user)
    other_online = is_online(course.instructor) if course.instructor else False

    return render(
        request,
        "students/student_instructor_chat.html",
        {
            "course": course,
            "chat": chat,
            "instructor": course.instructor,
            "other_online": other_online,
            "messages": [serialize_message(m, request.user, other_online) for m in chat.messages.all()],
            "reaction_emojis": REACTION_EMOJIS,
            "reaction_emojis_json": json.dumps(REACTION_EMOJIS),
            "poll_url": reverse("courses:chat_poll", args=[chat.id]),
            "react_url_template": reverse("courses:chat_react", args=[999999999]),
        }
    )


def _handle_chat_post(request, chat, notify_recipient, redirect_url, recipient_link):
    message_text = request.POST.get("message", "").strip()
    attachment = request.FILES.get("attachment")
    voice_note = request.FILES.get("voice_note")
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if not (message_text or attachment or voice_note):
        if is_ajax:
            return JsonResponse({"error": "Message is empty"}, status=400)
        return redirect(redirect_url)

    msg = InstructorStudentMessage.objects.create(
        chat=chat,
        sender=request.user,
        message=message_text,
        attachment=attachment,
        voice_note=voice_note,
    )

    if notify_recipient:
        label = "sent a file" if (attachment or voice_note) and not message_text else message_text
        notify(
            notify_recipient,
            f"{request.user.first_name or request.user.username}: {label}"[:255],
            link=recipient_link
        )

    if is_ajax:
        return JsonResponse({"message": serialize_message(msg, request.user, False)})

    return redirect(redirect_url)


@login_required
def chat_poll(request, chat_id):
    chat = get_object_or_404(InstructorStudentChat, id=chat_id)
    if request.user not in (chat.instructor, chat.student):
        return HttpResponseForbidden()

    other = chat.student if request.user == chat.instructor else chat.instructor
    mark_read(chat, request.user)
    other_online = is_online(other)

    since_id = request.GET.get("since")
    qs = chat.messages.all()
    if since_id:
        qs = qs.filter(id__gt=since_id)

    pending_own = chat.messages.filter(sender=request.user, is_read=False)

    return JsonResponse({
        "messages": [serialize_message(m, request.user, other_online) for m in qs],
        "pending_ticks": [
            {"id": m.id, "tick_state": tick_state(m, other_online)}
            for m in pending_own
        ],
        "other_online": other_online,
    })


@login_required
@require_http_methods(["POST"])
def chat_react(request, message_id):
    message = get_object_or_404(InstructorStudentMessage, id=message_id)
    chat = message.chat
    if request.user not in (chat.instructor, chat.student):
        return HttpResponseForbidden()

    emoji = request.POST.get("emoji", "").strip()
    if emoji not in REACTION_EMOJIS:
        return JsonResponse({"error": "Invalid reaction"}, status=400)

    existing = MessageReaction.objects.filter(message=message, user=request.user).first()
    if existing and existing.emoji == emoji:
        existing.delete()
    elif existing:
        existing.emoji = emoji
        existing.save(update_fields=["emoji"])
    else:
        MessageReaction.objects.create(message=message, user=request.user, emoji=emoji)

    reactions = {}
    for r in message.reactions.all():
        reactions.setdefault(r.emoji, []).append(r.user.username)

    return JsonResponse({
        "reactions": [
            {"emoji": emoji, "users": users, "count": len(users)}
            for emoji, users in reactions.items()
        ]
    })


@login_required
def student_download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    certificate = get_object_or_404(
        Certificate,
        student=request.user,
        course=course,
        is_active=True
    )

    logo_url = request.build_absolute_uri(static('images/logo.png'))
    seal_url = request.build_absolute_uri(static('images/seal.png'))

    # TEMPORARY DEBUG - remove after fixing
    print("=== LOGO URL:", logo_url)
    print("=== SEAL URL:", seal_url)

    return render(request, 'students/certificate.html', {
        'course': course,
        'student': request.user,
        'certificate': certificate,
        'logo_url': logo_url,
        'seal_url': seal_url,
    })
