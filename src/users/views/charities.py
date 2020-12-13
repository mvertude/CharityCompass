from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect

from ..decorators import charity_required, volunteer_required
from ..forms import CharitySignUpForm, EmailForm
from ..models import User, Charity
from events.models import Event
from notifications.models import Notification
from django.core.mail import send_mail, BadHeaderError, send_mass_mail

class CharitySignUpView(CreateView):
    model = User
    form_class = CharitySignUpForm
    template_name = 'users/charities/signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'charity'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('charities:charity_dashboard')
  

@login_required 
def charity_detail(request, slug):
    
    charity = get_object_or_404(Charity, slug=slug)
    is_favorite = False
    
    # does not list events because no reference to them
    '''
    if (request.user.is_charity):
        return render(request, 'users/charities/dashboard.html')
    '''

    if charity.favorite.filter(pk=request.user.id).exists():
        is_favorite = True
    
    context = {
        'charity': charity,
        'is_favorite': is_favorite
    }
    return render(request, 'users/charities/charity_page.html', context)


@method_decorator([login_required, charity_required], name='dispatch')
class EventCreateView(CreateView):
    model = Event
    fields = ('title', 
              'event_type', 
              'description', 
              'location', 
              'event_date', 
              'start_time', 
              'end_time')
    template_name = 'users/charities/event_create_form.html'


    def form_valid(self, form):
        event = form.save(commit=False)
        event.user = self.request.user
        event.owner = Charity.objects.get(user=self.request.user)
        event.save()
        #messages.success(self.request, 'The post was created!')
        return redirect('charities:charity_dashboard')


@method_decorator([login_required, charity_required], name='dispatch')
class DashboardView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'users/charities/dashboard.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = Event.objects.filter(user=self.request.user)
        return queryset.order_by('event_date')


class EventsDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        is_interested = False
        is_registered = False
        
        if self.object.interested.filter(pk=self.request.user.id).exists():
            is_interested = True
        if self.object.registered.filter(pk=self.request.user.id).exists():
            is_registered = True
      
        context['is_interested'] = is_interested
        context['is_registered'] = is_registered
        return context


@method_decorator([login_required, charity_required], name='dispatch')
class EventsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    fields = ('title', 
              'event_type', 
              'description', 
              'location', 
              'event_date', 
              'start_time', 
              'end_time')

    def get_success_url(self):
        registered_users = self.object.registered.all()
        for user in registered_users:
            Notification.objects.create(event=self.object, 
                                        sender=self.object.user, 
                                        event_name=self.object.title,
                                        receiver=user,
                                        notification_type=3,
                                        text_preview=' updated ')
            
        
        return reverse('charities:event_detail', kwargs={'pk': self.object.pk})

    #def form_valid(self, form):
      
     #   return super().form_valid(form)

    # test run by UserPassesTestMixin, check if the user is the author/charity_name of the event
    # IMPLEMENTATION DETAIL: other tests needed?
    # must change to be a valid test
    def test_func(self):
        return True

# delete event, need to connect to dashboard/users, templates, urls
#FIX, doesn't seem to work

@method_decorator([login_required, charity_required], name='dispatch')
class EventsDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    # success_url set to home page
    #success_url = '/'
    
    def get_success_url(self):
        registered_users = self.object.registered.all()
        for user in registered_users:
            event_name = self.object.title
            Notification.objects.create(event=self.object,
                                        event_name = event_name,
                                        sender=self.object.user, 
                                        receiver=user,
                                        notification_type=4,
                                        text_preview= ' deleted the event: ')
            
        
        return reverse('home')
    
    # must change to be a valid test
    def test_func(self):
        return True

@login_required
def send_newsletter(request):
    charity = get_object_or_404(Charity, user=request.user)
    favorited = charity.favorite.all()
    email_list = []
    for user in favorited:
        email_list.append(user.email)
    email_list.append(request.user.email)
    if request.method == 'GET':
        form = EmailForm()
    else:
        form = EmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                messages = []
                for email in email_list:
                    message_to_send = (charity.charity_name +': '+subject, message, 'charitycompassucsd@gmail.com', [email])
                    messages.append(message_to_send)
                #send_mail(charity.charity_name +': '+subject, message, 'charitycompassucsd@gmail.com', email_list)
                send_mass_mail(messages, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('charities:charity_dashboard')
    return render(request, "users/charities/email.html", {'form': form})

