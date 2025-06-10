from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Role, validate_email_domain
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validate_email_domain(email)
        return email

    role = forms.ModelChoiceField(
        queryset=Role.objects.exclude(name='administrador'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'role', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico (debe terminar con @uncuyo.edu.ar)'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
        }

class CustomUserChangeForm(UserChangeForm):

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validate_email_domain(email)
        return email

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'role')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico (debe terminar con @uncuyo.edu.ar)'
            }),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
        }