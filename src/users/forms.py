from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db import transaction

from users.models import Charity, Volunteer, User, UserSettings
from events.models import EventType

class VolunteerSignUpForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(widget=forms.TextInput( 
        attrs={'autofocus': True}))
    last_name = forms.CharField()
    interests = forms.ModelMultipleChoiceField(
        queryset=EventType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )


    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", 'username', 'email', "password1", "password2", "interests")

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)

        user.is_volunteer = True
        user.save()
        volunteer = Volunteer.objects.create(user=user, first_name=user.first_name, last_name=user.last_name)
        volunteer.interests.add(*self.cleaned_data.get('interests'))
        return user

class CharitySignUpForm(UserCreationForm):
    email = forms.EmailField()
    charity_name = forms.CharField(max_length=250, 
    widget=forms.TextInput( 
        attrs={'autofocus': True}))
    address = forms.CharField(max_length=200, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('charity_name', 'username', 'email', 'password1', 'password2', 'address')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_charity = True
        if commit:
          user.save()
          charity = Charity.objects.create(user=user, charity_name=self.cleaned_data['charity_name'])
        return user

class VolunteerInterestsForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ('interests',)
        widgets = {
            'interests': forms.CheckboxSelectMultiple
        }


class UserUpdateForm(forms.ModelForm):  # allows us to update username and email
    email = forms.EmailField();

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):  # allows us to update our image
    class Meta:
        model = UserSettings
        fields = ['image']


class CharityUpdateForm(forms.ModelForm):  # allows us to update username and email
    charity_name = forms.CharField(max_length=200)
    website = forms.URLField(max_length=200, required=False)
   
    class Meta:
        model = Charity
        fields = ['charity_name', 'website', 'description']


class VolunteerUpdateForm(forms.ModelForm):  # allows us to update username and email
    first_name = forms.CharField(widget=forms.TextInput( 
        attrs={'autofocus': True}))
    last_name = forms.CharField()
    class Meta:
        model = Volunteer
        fields = ['first_name', 'last_name']


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={}), required=False, label='Old Password')
    new_password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={}), required=False, label='New Password')
    new_password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={}), required=False, label='Confirm New Password')
    
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class EmailForm(forms.Form):
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)