from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from users.decorators import charity_required, volunteer_required
from notifications.models import Notification
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404, render, reverse
from users.models import User, Charity, Volunteer
# Create your views here.

@method_decorator([login_required], name='dispatch')
class NotificationListView(ListView):
    model = Notification
    template_name = 'notification_list.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'notifications'
    #paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_charity:
            user = get_object_or_404(Charity, user=self.request.user)
        else:
            user = get_object_or_404(Volunteer, user=self.request.user)
        return Notification.objects.filter(receiver=user.user).order_by('-date')

def clear_all_notifications(request):
    notifications = Notification.objects.filter(receiver=request.user)
    for notification in notifications:
        notification.delete()
        #Notification.objects.remove(notification)
    
    if request.user.is_charity:
        return redirect('charities:charity_dashboard')
    else:
        return redirect('volunteers:volunteer_dashboard')