from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))

    # fields and db table to show on the form
    class Meta:
        model = Account
        fields = ['first_name', 'last_name',
                  'phone_number', 'email', 'password']

    # implement a bootstrap class on the form instead of manually setting the 'class:form-control' done in password
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        # shows placeholder message
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address '

        # loops thru all the form fields and use form-control bootstrap class
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    # checks if password is confirmed or not

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Set and Confirmation Passwords do not match."
            )


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']

    # implement a bootstrap class on the form instead of manually setting the 'class:form-control' done in password
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        # loops thru all the form fields and use form-control bootstrap class for each instead of manual setting iup
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    # removes the default label and image filename
    profile_picture = forms.ImageField(required=False, error_messages={
                                       'Invalid': ("Image files only.")}, widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2', 'city',
                  'state', 'country', 'profile_picture']

        # implement a bootstrap class on the form instead of manually setting the 'class:form-control' done in password
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # loops thru all the form fields and use form-control bootstrap class for each instead of manual setting iup
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
