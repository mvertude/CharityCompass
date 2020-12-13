from django.shortcuts import redirect, render
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required 
from django.db.models import Q 
from itertools import chain
from ..models import Charity
from events.models import Event
from ..forms import (UserUpdateForm, 
                    ProfileUpdateForm, 
                    VolunteerUpdateForm, 
                    CharityUpdateForm)

def home(request):
    if request.user.is_authenticated:
        if request.user.is_charity:
            return redirect('charities:charity_dashboard')
        else:
            return redirect('volunteers:volunteer_dashboard')
    return redirect('login')


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        pic_form = ProfileUpdateForm(request.POST,
                                    request.FILES,
                                    instance=request.user.usersettings)
        if request.user.is_charity:
            x_form = CharityUpdateForm(request.POST, instance=request.user.charity)
        else:
            x_form = VolunteerUpdateForm(request.POST, instance=request.user.volunteer)  
        
        if user_form.is_valid() and pic_form.is_valid():
            user_form.save()
            pic_form.save()
            x_form.save()
            messages.success(request, f'Your account has been updated!')

            if request.user.is_charity:
                return redirect('charities:charity_settings')
            else:
                return redirect('volunteers:volunteer_settings') 
        
    else:
        user_form = UserUpdateForm(instance=request.user)
        pic_form = ProfileUpdateForm(instance=request.user.usersettings)

        if request.user.is_charity:    
            x_form = CharityUpdateForm(instance=request.user.charity)
        else:    
            x_form = VolunteerUpdateForm(instance=request.user.volunteer)
     
    context = {
        'u_form': user_form,
        'p_form': pic_form,
        'x_form': x_form,
    }

    return render(request, 'users/settings.html', context)

@login_required
def update_password(request):
    if request.method == 'POST':
        pass_form = PasswordChangeForm(request.user, request.POST)
        if pass_form.is_valid():
                user = pass_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, f'Your password has been updated!')
                return redirect('update_password')

        
            
    else:
        pass_form = PasswordChangeForm(request.user)
    context = {
        'pass_form': pass_form
    }

    return render(request, 'users/password_settings.html', context)


class SearchResultsView(ListView):
    model = Charity
    template_name = 'users/search_results.html'

    def get_queryset(self): # new
        query = self.request.GET.get('q')
        event_list = Event.objects.filter(
            Q(title__icontains=query)
        )
        charity_list = Charity.objects.filter(
            Q(charity_name__icontains=query)
        )
        object_list = chain(event_list, charity_list)
        return object_list