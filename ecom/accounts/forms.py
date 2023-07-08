from django import forms

class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=12)
    password = forms.CharField(widget=forms.PasswordInput)
