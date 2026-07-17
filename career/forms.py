from django import forms
from .models import JobRole
from courses.models import Skill


class JobRoleForm(forms.ModelForm):
    # Manual input field
    skills_text = forms.CharField(
        label="Required Skills",
        required=False,
        help_text="Enter skills separated by commas (e.g. Linux, Git, Docker)",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Linux, Git, Docker"
        })
    )

    class Meta:
        model = JobRole
        fields = ['title', 'min_readiness', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill skills when editing
        if self.instance.pk:
            skills = self.instance.required_skills.all()
            self.fields['skills_text'].initial = ", ".join(
                skill.name for skill in skills
            )

    def save(self, commit=True):
        job_role = super().save(commit=False)

        if commit:
            job_role.save()

        # Handle skills
        skills_input = self.cleaned_data.get("skills_text", "")
        skill_names = [s.strip() for s in skills_input.split(",") if s.strip()]

        job_role.required_skills.clear()

        for name in skill_names:
            skill, _ = Skill.objects.get_or_create(
                name=name,
                defaults={"is_active": True}
            )
            job_role.required_skills.add(skill)

        return job_role
