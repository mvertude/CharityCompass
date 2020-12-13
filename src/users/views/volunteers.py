from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView

from ..decorators import volunteer_required
from ..forms import (VolunteerSignUpForm, 
                    VolunteerInterestsForm, 
                    UserUpdateForm, 
                    ProfileUpdateForm,
                    PasswordChangeForm)
from ..models import User, Volunteer, Charity
from events.models import EventType, Event
from notifications.models import Notification


class VolunteerSignUpView(CreateView):
    model = User
    form_class = VolunteerSignUpForm
    template_name = 'users/volunteers/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'volunteer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('volunteers:volunteer_dashboard')


@method_decorator([login_required, volunteer_required], name='dispatch')
class DashboardView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'users/volunteers/dashboard.html'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        interested_events = user.interested_events.all()
        registered_events = user.registered_volunteers.all()
        events = interested_events | registered_events
        return events


@method_decorator([login_required, volunteer_required], name='dispatch')
class VolunteerInterestsView(UpdateView):
    model = Volunteer
    form_class = VolunteerInterestsForm
    template_name = 'users/volunteers/interests_form.html'
    success_url = reverse_lazy('volunteers:volunteer_interests')

    def get_object(self):
        return self.request.user.volunteer

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)    


@login_required
@volunteer_required
def favorite_charity(request, slug):
    charity = get_object_or_404(Charity, slug=slug)

    if charity.favorite.filter(pk=request.user.id).exists():
        charity.favorite.remove(request.user)
    else:
        charity.favorite.add(request.user)
    
    return HttpResponseRedirect(charity.get_absolute_url())


@login_required
@volunteer_required
def interest_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if event.interested.filter(pk=request.user.id).exists():
        event.interested.remove(request.user)

    else:
        event.interested.add(request.user)
    
    return HttpResponseRedirect(event.get_absolute_url())


@login_required
@volunteer_required
def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    # unregister
    if event.registered.filter(pk=request.user.id).exists():
        event.registered.remove(request.user)
        Notification.objects.create(event=event, 
                                    event_name=event.title,
                                    sender=request.user, 
                                    receiver=event.user,
                                    notification_type=2,
                                    text_preview=' unregistered for ')
        
    # register
    else:
        event.interested.remove(request.user)
        event.registered.add(request.user)
        Notification.objects.create(event=event, 
                                    sender=request.user, 
                                    event_name=event.title,
                                    receiver=event.user,
                                    notification_type=1,
                                    text_preview=' registered for ')
    
    return HttpResponseRedirect(event.get_absolute_url())


@method_decorator([login_required, volunteer_required], name='dispatch')
class VolunteerNowView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'users/volunteers/volunteer_now_list.html'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        volunteer = self.request.user.volunteer
        volunteer_interests = volunteer.interests.values_list('pk', flat=True)
        interested_events = user.interested_events.all()
        registered_events = user.registered_volunteers.all()
        favorited_charities = user.favorite_charity.all()
        
        from_favorites = Event.objects.none()
        for charity in favorited_charities:
            from_favorites = from_favorites | Event.objects.filter(owner=charity)

        from_interests = Event.objects.filter(event_type__in=volunteer_interests)
        event_recommendations = (from_interests | from_favorites) \
        .exclude(id__in=interested_events) \
        .exclude(id__in=registered_events) 
        
        return event_recommendations.distinct().order_by('event_date')
        
    