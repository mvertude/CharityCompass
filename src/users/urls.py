from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import charities, users, volunteers

urlpatterns = [
    path('', users.home, name='home'),
    path('reset-password/', 
        auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
        name='reset_password'),
    path('reset-password-sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_sent.html'), 
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_form.html'), 
        name='password_reset_confirm'),
    path('reset-password-complete/', 
    auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_done.html'), 
    name='password_reset_complete'),
    path('settings/password-update/', users.update_password, name='update_password'),

    path('search/', users.SearchResultsView.as_view(), name='search_results'),
    

    path('charities/', include(([
        path('', charities.DashboardView.as_view(), name='charity_dashboard'),
        path('settings/', users.profile, name='charity_settings'),
        path('user/<slug:slug>/', charities.charity_detail, name='charity_page'),
        path('event/<int:pk>/', charities.EventsDetailView.as_view(), name='event_detail'),
        path('event/add/', charities.EventCreateView.as_view(), name='event_add'),
        path('send-newsletter/', charities.send_newsletter, name='send_newsletter'),
        path('event/<int:pk>/update', charities.EventsUpdateView.as_view(), name='event_update'),
        path('event/<int:pk>/delete', charities.EventsDeleteView.as_view(), name='event_delete'),
    ], 'users'), namespace='charities')),

    
    path('volunteers/', include(([
        path('', volunteers.DashboardView.as_view(), name='volunteer_dashboard'),
        path('interests/', volunteers.VolunteerInterestsView.as_view(), name='volunteer_interests'),
        path('settings/', users.profile, name='volunteer_settings'),
        path('favorite-charity/<slug:slug>', volunteers.favorite_charity, name='favorite_charity'),
        path('interest-event/<int:pk>/', volunteers.interest_event, name='interest_event'),
        path('register-event/<int:pk>/', volunteers.register_event, name='register_event'),
        path('volunteer-now/', volunteers.VolunteerNowView.as_view(), name='volunteer_now'),
        
    ], 'users'), namespace='volunteers')),
]


