from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect


from accounts.notifications import notify_all_students, notify_students_of_instructor
from career.forms import JobRoleForm
from career.services import calculate_job_readiness
from instructors.decorators import instructor_required
from .models import JobRole

@staff_member_required
def job_roles_list(request):
    roles = JobRole.objects.all()
    return render(request, "adminpanel/job_roles.html", {
        "roles": roles
    })

@staff_member_required
def job_role_create(request):
    form = JobRoleForm(request.POST or None)

    if form.is_valid():
        role = form.save()
        notify_all_students(f"New job role added: {role.title}")
        return redirect("career_job_roles")

    return render(request, "adminpanel/job_role_form.html", {
        "form": form,
        "title": "Create Job Role"
    })


@staff_member_required
def job_role_edit(request, pk):
    role = get_object_or_404(JobRole, pk=pk)
    form = JobRoleForm(request.POST or None, instance=role)

    if form.is_valid():
        form.save()
        return redirect("career_job_roles")

    return render(request, "adminpanel/job_role_form.html", {
        "form": form,
        "title": "Edit Job Role"
    })


@instructor_required
def instructor_job_roles_list(request):
    roles = JobRole.objects.all()
    return render(request, "instructors/job_roles.html", {
        "roles": roles
    })


@instructor_required
def instructor_job_role_create(request):
    form = JobRoleForm(request.POST or None)

    if form.is_valid():
        role = form.save()
        notify_students_of_instructor(request.user, f"New job role added: {role.title}")
        return redirect("instructor_job_roles")

    return render(request, "instructors/job_role_form.html", {
        "form": form,
        "title": "Create Job Role"
    })


@instructor_required
def instructor_job_role_edit(request, pk):
    role = get_object_or_404(JobRole, pk=pk)
    form = JobRoleForm(request.POST or None, instance=role)

    if form.is_valid():
        form.save()
        return redirect("instructor_job_roles")

    return render(request, "instructors/job_role_form.html", {
        "form": form,
        "title": "Edit Job Role"
    })


def get_job_suggestions(student):
    suggestions = []

    for role in JobRole.objects.filter(is_active=True):
        readiness = calculate_job_readiness(student, role)

        if readiness >= role.min_readiness:
            suggestions.append({
                "role": role.title,
                "readiness": readiness
            })

    return suggestions