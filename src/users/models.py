from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from PIL import Image
from django.urls import reverse
from django.utils.text import slugify

import events.models 
# Create your models here.

class User(AbstractUser):
    is_charity = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)


class Volunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    interests = models.ManyToManyField('events.EventType', related_name='event_type_volunteer')
    
    def __str__(self):
        return self.user.username


class Charity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    charity_name = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(default='',blank=True)
    favorite = models.ManyToManyField(User, related_name='favorite_charity', blank=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('charities:charity_page', args=[self.slug])

def create_slug(instance, new_slug=None):
    slug = slugify(instance.charity_name)
    if new_slug is not None:
        slug = new_slug
    qs = Charity.objects.filter(slug=slug).order_by("-user_id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().user_id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_charity_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_charity_receiver, sender=Charity)

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    
    def __str__(self):
        return f"{self.user.username}'s Settings"
        
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


'''
class FavoriteCharity(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, related_name='favorite_charities')
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE, related_name='favorite_charities')
'''
