from django.db.models.signals import post_save
#from django.contrib.auth.models import User  # the sender because it sends the signal
from django.dispatch import receiver  # receiver from the sender
from .models import UserSettings, User


@receiver(post_save, sender=User)  # decorator
def create_settings(sender, instance, created, **kwargs):
    if created:  # user was created, create a profile object
        UserSettings.objects.create(user=instance)


@receiver(post_save, sender=User)  # decorator
def save_settings(sender, instance, **kwargs):  # kwargs accepts any additional keyword arguments
    instance.usersettings.save()

