from django.contrib import admin
from .models import JobRole

@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'min_readiness', 'is_active')
    filter_horizontal = ('required_skills',)
