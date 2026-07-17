from django.urls import path
from .views import (
    job_role_create,
    job_role_edit,
    job_roles_list,
    instructor_job_roles_list,
    instructor_job_role_create,
    instructor_job_role_edit,
)

urlpatterns = [
    path('job-roles/', job_roles_list, name='career_job_roles'),
    path('job-roles/create/', job_role_create, name='career_job_role_create'),
    path('job-roles/<int:pk>/edit/', job_role_edit, name='career_job_role_edit'),

    path('instructor/job-roles/', instructor_job_roles_list, name='instructor_job_roles'),
    path('instructor/job-roles/create/', instructor_job_role_create, name='instructor_job_role_create'),
    path('instructor/job-roles/<int:pk>/edit/', instructor_job_role_edit, name='instructor_job_role_edit'),
]
