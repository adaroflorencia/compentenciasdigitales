from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


def validate_email_domain(email):
    """Valida que el email termine con @uncuyo.edu.ar"""
    allowed_domain = '@uncuyo.edu.ar'
    if not email.endswith(allowed_domain):
        raise ValidationError(f'El correo electrónico debe terminar con {allowed_domain}')


class Role(models.Model):
    ROLE_CHOICES = (
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('no_docente', 'No Docente'),
        ('administrador', 'Administrador')
    )

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        validate_email_domain(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def clean(self):
        super().clean()
        if self.email and not self.pk:
            validate_email_domain(self.email)
        elif self.email and self.pk:
            try:
                original = CustomUser.objects.get(pk=self.pk)
                if original.email != self.email:
                    validate_email_domain(self.email)
            except CustomUser.DoesNotExist:
                pass

    def __str__(self):
        return self.email