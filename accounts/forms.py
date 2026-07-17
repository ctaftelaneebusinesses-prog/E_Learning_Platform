import re

from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

PHONE_RE = re.compile(r'^\+?[0-9\s\-]{7,20}$')
LINKEDIN_RE = re.compile(r'^https?://(www\.)?linkedin\.com/.+$', re.IGNORECASE)
GITHUB_RE = re.compile(r'^https?://(www\.)?github\.com/.+$', re.IGNORECASE)

MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_PROFILE_IMAGE_TYPES = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    role = forms.ChoiceField(
        choices=[
            ('STUDENT', 'Student'),
            ('INSTRUCTOR', 'Instructor'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_active = False  # locked until an admin approves the registration

        if commit:
            user.save()
            user.profile.role = self.cleaned_data['role']
            user.profile.approval_status = 'PENDING'
            user.profile.save()

        return user


class CustomSocialSignupForm(SocialSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ProfileUpdateForm(forms.Form):
    """Handles the fields on User + Profile together for the profile page."""

    full_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    institution_name = forms.CharField(max_length=255, required=False)
    linkedin_url = forms.CharField(max_length=300, required=False)
    github_url = forms.CharField(max_length=300, required=False)
    education_type = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, user=None, role='STUDENT', **kwargs):
        self.user = user
        self.role = role
        super().__init__(*args, **kwargs)

        from .models import Profile
        self.fields['education_type'].choices = Profile.EDUCATION_TYPE_CHOICES

        # Admins only manage name, email and picture.
        if self.role == 'ADMIN':
            del self.fields['phone_number']
            del self.fields['institution_name']
            del self.fields['linkedin_url']
            del self.fields['github_url']
            del self.fields['education_type']
        elif self.role != 'STUDENT':
            del self.fields['education_type']

    def clean_full_name(self):
        return self.cleaned_data['full_name'].strip()

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone and not PHONE_RE.match(phone):
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

    def clean_linkedin_url(self):
        url = self.cleaned_data.get('linkedin_url', '').strip()
        if url and not LINKEDIN_RE.match(url):
            raise forms.ValidationError("Enter a valid LinkedIn profile URL (e.g. https://linkedin.com/in/username).")
        return url

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url', '').strip()
        if url and not GITHUB_RE.match(url):
            raise forms.ValidationError("Enter a valid GitHub profile URL (e.g. https://github.com/username).")
        return url

    def save(self):
        cleaned = self.cleaned_data
        user = self.user
        user.first_name = cleaned['full_name']
        user.email = cleaned['email']
        user.save()

        profile = user.profile
        if self.role != 'ADMIN':
            profile.phone_number = cleaned.get('phone_number', '')
            profile.institution_name = cleaned.get('institution_name', '')
            profile.linkedin_url = cleaned.get('linkedin_url', '')
            profile.github_url = cleaned.get('github_url', '')
        if self.role == 'STUDENT':
            profile.education_type = cleaned.get('education_type', '')
        profile.save()
        return user


class ProfilePictureForm(forms.Form):
    profile_image = forms.ImageField(required=True)

    def clean_profile_image(self):
        image = self.cleaned_data['profile_image']

        if image.size > MAX_PROFILE_IMAGE_SIZE:
            raise forms.ValidationError("Image must be smaller than 5 MB.")

        content_type = getattr(image, 'content_type', '') or ''
        if content_type.lower() not in ALLOWED_PROFILE_IMAGE_TYPES:
            raise forms.ValidationError("Only JPG, JPEG, PNG and WebP images are allowed.")

        return image


class ProfileCompletionForm(forms.Form):
    """Mandatory first-login onboarding form (see accounts.middleware.ProfileCompletionMiddleware)."""

    full_name = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'})
    )
    profile_image = forms.ImageField(required=False)
    education_type = forms.ChoiceField(
        choices=[], required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, user=None, role='STUDENT', **kwargs):
        self.user = user
        self.role = role
        super().__init__(*args, **kwargs)

        from .models import Profile
        self.fields['education_type'].choices = Profile.EDUCATION_TYPE_CHOICES

        if self.role == 'ADMIN':
            del self.fields['phone_number']
            del self.fields['education_type']
        elif self.role != 'STUDENT':
            del self.fields['education_type']
        else:
            self.fields['education_type'].required = True

        if self.role != 'ADMIN':
            self.fields['phone_number'].required = True

    def clean_full_name(self):
        return self.cleaned_data['full_name'].strip()

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone and not PHONE_RE.match(phone):
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if not image:
            return image

        if image.size > MAX_PROFILE_IMAGE_SIZE:
            raise forms.ValidationError("Image must be smaller than 5 MB.")

        content_type = getattr(image, 'content_type', '') or ''
        if content_type.lower() not in ALLOWED_PROFILE_IMAGE_TYPES:
            raise forms.ValidationError("Only JPG, JPEG, PNG and WebP images are allowed.")

        return image

    def save(self):
        cleaned = self.cleaned_data
        user = self.user
        user.first_name = cleaned['full_name']
        user.save()

        profile = user.profile
        if self.role != 'ADMIN':
            profile.phone_number = cleaned.get('phone_number', '')
        if self.role == 'STUDENT':
            profile.education_type = cleaned.get('education_type', '')
        if cleaned.get('profile_image'):
            profile.profile_image = cleaned['profile_image']
        profile.profile_completed = True
        profile.save()
        return user


class ProfileChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
