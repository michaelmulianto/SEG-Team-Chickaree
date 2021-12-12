"""
Define the forms for the system. Forms take data and utilise it for a certain
purpose like loggin in a user with the correct username and password.

"""

from django import forms
from clubs.models import User, Club, Application, Tournament
from django.core.validators import RegexValidator


class LogInForm(forms.Form):
    """Form to grant access to a returning user's personalised content"""
    email = forms.CharField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class SignUpForm(forms.ModelForm):
    """Form to allow a visitor to make an account and become a registered user"""
    class Meta:
        model = User
        # If we do not specify fields, it will use all of them.
        # We don't want to include password as we use 2 fields
        fields = ['first_name', 'last_name', 'username', 'email', 'experience', 'bio']
        widgets = {'bio': forms.Textarea()}

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
        return club

class ApplyToClubForm(forms.ModelForm):

    class Meta:
        model = Application
        fields = ['personal_statement']
        widgets = {'personal_statement': forms.Textarea()}

    def save(self, desired_club, current_user):
        super().save(commit=False)
        application = Application.objects.create(
            club = desired_club,
            user = current_user,
            personal_statement = self.cleaned_data.get('personal_statement'),
        )
        return application

class EditAccountForm(forms.ModelForm):
    class Meta:
        model = User
        #only want to make these 4 fields editable
        fields = ['username', 'first_name', 'last_name', 'email']

class EditClubInfoForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'location', 'description']
        widgets = {'description': forms.Textarea()}

class OrganiseTournamentForm(forms.ModelForm): #2,4,8,16,24,32,48,96
    class Meta:
        model = Tournament
        fields = ['name', 'description', 'capacity', 'deadline', 'start', 'end']
        deadline = forms.DateTimeField(input_formats=['%y-%m-%d %H:%M:%S'])
        start = forms.DateTimeField(input_formats=['%y-%m-%d %H:%M:%S'])
        end = forms.DateTimeField(input_formats=['%y-%m-%d %H:%M:%S'])

        capacity_choices = (
            ('2','2'),
            ('4','4'),
            ('8','8'),
            ('16','16'),
            ('24','24'),
            ('32','32'),
            ('48','48'),
            ('96','96'),
        )

        capacity = forms.ChoiceField(choices = capacity_choices)
        widgets = {'description': forms.Textarea()}

    #Create new tournament using the tournament form data
    def save(self, desired_club):
        super().save(commit=False)
        tournament = Tournament.objects.create(
            club = desired_club,
            name = self.cleaned_data.get('name'),
            description = self.cleaned_data.get('description'),
            capacity = self.cleaned_data.get('capacity'),
            deadline = self.cleaned_data.get('deadline'),
            start = self.cleaned_data.get('start'),
            end = self.cleaned_data.get('end')
        )
        return tournament
