from django.contrib import admin
from .models import Charity, User, Volunteer

# Register your models here.
admin.site.register(User)
admin.site.register(Volunteer)
admin.site.register(Charity)