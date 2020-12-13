from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.db.models.signals import post_save, post_delete
from notifications.models import Notification
import users.models

# Create your models here.
class EventType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Event(models.Model):
    user = models.ForeignKey(users.models.User, on_delete=models.CASCADE, related_name='events')
    owner = models.ForeignKey(users.models.Charity, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=80)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='events') 
    event_date = models.CharField(max_length=60)
    description = models.TextField()
    location = models.CharField(max_length=60)
    start_time = models.TimeField(auto_now=False, auto_now_add=False) 
    end_time = models.TimeField(auto_now=False, auto_now_add=False)

    interested = models.ManyToManyField(users.models.User, related_name='interested_events', blank=True)
    registered = models.ManyToManyField(users.models.User, related_name='registered_volunteers', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('charities:event_detail', kwargs={'pk': self.pk})

