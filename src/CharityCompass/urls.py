"""CharityCompass URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.conf import settings
from users.views import charities, users, volunteers
from django.conf.urls.static import static

from notifications.views import NotificationListView, clear_all_notifications


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/login.html'), name='logout'),
    path('', include('users.urls')),
    path('signup/volunteer/', volunteers.VolunteerSignUpView.as_view(), name='volunteer_signup'),
    path('signup/charity', charities.CharitySignUpView.as_view(), name='charity_signup'), 
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('clear-notifications/', clear_all_notifications, name='clear_notifications'),
]

if settings.DEBUG:  # if currently in DEBUG mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
