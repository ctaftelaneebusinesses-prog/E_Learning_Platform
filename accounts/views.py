from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import (
    ProfileChangePasswordForm,
    ProfileCompletionForm,
    ProfilePictureForm,
    ProfileUpdateForm,
    UserRegisterForm,
)
from .models import Notification
from .notifications import notify
from .themes import get_theme
from utils.activity_logger import log_user_registration


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_user_registration(user, request)

            for admin in User.objects.filter(profile__role='ADMIN'):
                notify(
                    admin,
                    f"New {user.profile.role.title()} registration from {user.username} is awaiting approval.",
                    link=reverse('admin_user_list'),
                )

            messages.success(
                request,
                "Account created successfully. An admin needs to approve your registration before you can log in."
            )
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(
        request,
        'auth/register.html',
        {'form': form}
    )


def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        username = identifier
        if '@' in identifier:
            matched_user = User.objects.filter(email__iexact=identifier).first()
            if matched_user:
                username = matched_user.username

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('dashboard_redirect')

        candidate = User.objects.filter(username=username).first()
        if candidate and candidate.check_password(password) and not candidate.is_active:
            approval_status = getattr(candidate.profile, 'approval_status', 'APPROVED')
            if approval_status == 'REJECTED':
                messages.error(
                    request,
                    "Your registration was rejected by an admin. Please contact support for details."
                )
            else:
                messages.error(
                    request,
                    "Your registration is awaiting admin approval. You'll be able to log in once it's approved."
                )
        else:
            messages.error(
                request,
                "Invalid username or password"
            )

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_redirect(request):
    role = request.user.profile.role
    print("DEBUG ROLE:", role)

    if role == 'ADMIN':
        return redirect('admin_dashboard')

    elif role == 'INSTRUCTOR':
        return redirect('instructor_dashboard')

    else:
        return redirect('student_dashboard')


def _form_errors(form):
    return {field: [str(err) for err in errs] for field, errs in form.errors.items()}


def _profile_data(user):
    profile = user.profile

    data = {
        'full_name': user.first_name,
        'username': user.username,
        'email': user.email,
        'role': profile.role,
        'profile_image_url': profile.profile_image.url if profile.profile_image else '',
    }

    if profile.role != 'ADMIN':
        data.update({
            'phone_number': profile.phone_number,
            'institution_name': profile.institution_name,
            'linkedin_url': profile.linkedin_url,
            'github_url': profile.github_url,
        })

    if profile.role == 'STUDENT':
        theme = get_theme(profile.education_type)
        data.update({
            'education_type': profile.education_type,
            'theme_css_class': theme['css_class'],
        })

    return data


@login_required
def profile_view(request):
    from .models import Profile

    return render(
        request,
        'accounts/profile.html',
        {
            'profile_data': _profile_data(request.user),
            'education_type_choices': Profile.EDUCATION_TYPE_CHOICES,
        }
    )


@login_required
def complete_profile_view(request):
    profile = request.user.profile

    if profile.profile_completed:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = ProfileCompletionForm(
            request.POST,
            request.FILES,
            user=request.user,
            role=profile.role
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile is all set!")
            return redirect('dashboard_redirect')
    else:
        form = ProfileCompletionForm(user=request.user, role=profile.role)

    return render(request, 'accounts/complete_profile.html', {'form': form})


@login_required
@require_http_methods(['GET'])
def api_get_profile(request):
    return JsonResponse({'success': True, 'data': _profile_data(request.user)})


@login_required
@require_http_methods(['POST'])
def api_update_profile(request):
    form = ProfileUpdateForm(
        request.POST,
        user=request.user,
        role=request.user.profile.role
    )

    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully.',
            'data': _profile_data(request.user)
        })

    return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)


@login_required
def notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return redirect(notification.link or 'dashboard_redirect')


@login_required
@require_http_methods(['POST'])
def notifications_mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER') or 'dashboard_redirect')


@login_required
@require_http_methods(['POST'])
def api_upload_picture(request):
    form = ProfilePictureForm(request.POST, request.FILES)

    if form.is_valid():
        profile = request.user.profile
        profile.profile_image = form.cleaned_data['profile_image']
        profile.save()
        return JsonResponse({
            'success': True,
            'message': 'Profile picture updated successfully.',
            'image_url': profile.profile_image.url
        })

    return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)


@login_required
@require_http_methods(['POST'])
def api_change_password(request):
    if request.user.profile.role == 'ADMIN':
        return JsonResponse({
            'success': False,
            'errors': {'__all__': ['Password change is not available for admin accounts here.']}
        }, status=403)

    form = ProfileChangePasswordForm(user=request.user, data=request.POST)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return JsonResponse({'success': True, 'message': 'Password changed successfully.'})

    return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
