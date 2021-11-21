"""
Define the forms for the system. Forms take data and utilise it for a certain
purpose like loggin in a user with the correct username and password.

Currently implemented forms:
    - SignUpForm
    - LogInForm
"""

from django import forms
from clubs.models import User, Club, Application
from django.core.validators import RegexValidator

"""Form to grant access to a returning user's personalised content"""
class LogInForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class SignUpForm(forms.ModelForm):
    """Form to allow a visitor to make an account and become a registered user"""
    class Meta:
        model = User
        # If we do not specify fields, it will use all of them.
        # We don't want to include password as we use 2 fields
        fields = ['first_name', 'last_name', 'username', 'email']

    # Define fields excluded in Meta
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        validators=[RegexValidator(
            regex=r'[A-Z]',
            message='Password must contain an uppercase character.'
            ),
            RegexValidator(
            regex=r'[a-z]',
            message='Password must contain a lowercase character.'
            ),
            RegexValidator(
            regex=r'[0-9]',
            message='Password must contain a number.'
            ),
            ]
        )
    password_confirmation = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    # Verify our custom fields are valid.
    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    # Create new user using form data.
    def save(self):
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name = self.cleaned_data.get('first_name'),
            last_name = self.cleaned_data.get('last_name'),
            email = self.cleaned_data.get('email'),
            password = self.cleaned_data.get('new_password'),
        )
        return user

class CreateClubForm(forms.ModelForm):

    class Meta:
        model = Club
        fields = ['name', 'location', 'description']
        widgets = {'description': forms.Textarea()}

    #Create new club using the club form data
    def save(self):
        super().save(commit=False)
        club = Club.objects.create(
            name = self.cleaned_data.get('name'),
            location = self.cleaned_data.get('location'),
            description = self.cleaned_data.get('description'),
        )

class ApplyToClubForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['experience', 'personalStatement']
        widgets = {'personalStatement': forms.Textarea()}

        # def save(self, *args, **kwargs):
        #     if not(Application.objects.filter(club=desired_club, user = current_user).exists()) and not(Member.objects.filter(club=desired_club, user = current_user).exists()):
        #         super().save(*args, **kwargs, commit=False)
        #         application = Application.objects.create(
        #             club = kwargs["club"],
        #             user = kwargs["user"],
        #             experience = self.cleaned_data.get('experience'),
        #             personalStatement = self.cleaned_data.get('personalStatement'),
        #         )
