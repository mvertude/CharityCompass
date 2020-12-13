from django.db import models
import events.models
from users.models import User
# Create your models here.

class Notification(models.Model):
    NOTIFICATION_TYPES = ((1, 'Registered'), 
                        (2, 'Unregistered'), 
                        (3, 'Updated_Event'),
                        (4, 'Deleted_Event'))

    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, related_name='notification', blank=True, null=True)
    event_name = models.CharField(max_length=90, default='')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='noti_from_user')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='noti_to_user')
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    text_preview = models.CharField(max_length=90, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)