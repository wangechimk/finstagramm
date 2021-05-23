from django import forms
from .models import Image
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class uploadForm(forms.ModelForm):
    class Meta:
        model = Image
        exclude = ['profile', 'likes', 'created_on']

class SignUpForm(UserCreationForm):
    username   = forms.CharField(widget=(forms.TextInput(attrs={'class': 'signup-form', 'placeholder': 'Username'})),label='')
    first_name = forms.CharField(widget=(forms.TextInput(attrs={'class': 'signup-form', 'placeholder': 'Full Name'})),label='', max_length=32)
    email      = forms.EmailField(widget=(forms.EmailInput(attrs={'class': 'signup-form', 'placeholder': 'Email'})),label='', max_length=64)
    password1  = forms.CharField(widget=(forms.PasswordInput(attrs={'class': 'signup-form', 'placeholder': 'Password'})),label='')
    password2  = forms.CharField(widget=(forms.PasswordInput(attrs={'class': 'signup-form', 'placeholder': 'Password Again'})),label='')

    def clean(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Another account is using {email}")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username isn't available. Please try another.")

        return self.cleaned_data

    class Meta:
        model = User
        fields = ('email', 'first_name','username', 'password1','password2')


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=(forms.TextInput(attrs={'class': 'signup-form', 'placeholder': 'Username'})),label='')
    password = forms.CharField(widget=(forms.PasswordInput(attrs={'class': 'signup-form', 'placeholder': 'Password'})),label='')
