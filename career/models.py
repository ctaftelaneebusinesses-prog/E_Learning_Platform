from django.db import models
from courses.models import Skill

class JobRole(models.Model):
    title = models.CharField(max_length=150, unique=True)

    required_skills = models.ManyToManyField(
        Skill,
        related_name='job_roles'
    )

    min_readiness = models.PositiveIntegerField(
        default=70,
        help_text="Minimum % readiness to suggest this job"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
