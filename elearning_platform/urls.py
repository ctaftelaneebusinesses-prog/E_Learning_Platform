# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# from accounts.views import dashboard_redirect
# from .views import home

# urlpatterns = [
#     # 🏠 Home
#     path('', home, name='home'),

#     # ✅ CUSTOM APPS (FIRST)
#     path('career/', include('career.urls')),
#     path('courses/', include('courses.urls')),
#     path('accounts/', include('accounts.urls')),
#     path('admin-panel/', include('adminpanel.urls')),
#     path('instructor/', include('instructors.urls')),
#     path('student/', include('students.urls')),
#     path('mentor-ai/', include('mentor_ai.urls')),
#     path('dashboard/', dashboard_redirect, name='dashboard_redirect'),

#     # ❌ DJANGO ADMIN (ALWAYS LAST)
#     path('admin/', admin.site.urls),
# ]

# # ✅ Serve media files in development
# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL,
#         document_root=settings.MEDIA_ROOT
#     )
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import dashboard_redirect
from .views import home

urlpatterns = [
    # 🏠 Home
    path('', home, name='home'),

    # ✅ CUSTOM APPS (FIRST)
    path('career/', include('career.urls')),
    path('courses/', include('courses.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/social/', include('allauth.urls')),
    path('admin-panel/', include('adminpanel.urls')),
    path('instructor/', include('instructors.urls')),
    path('student/', include('students.urls')),
    path('mentor-ai/', include('mentor_ai.urls')),
    path('messages/', include('messaging.urls')),
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),

    # ❌ DJANGO ADMIN (ALWAYS LAST)
    path('admin/', admin.site.urls),
]

# ✅ Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])