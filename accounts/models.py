from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from iso3166 import countries


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("l'adresse email est obligatoire.")

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        kwargs["is_active"] = True

        return self.create_user(email=email, password=password, **kwargs)



class Shopper(AbstractUser):
    username = None
    email = models.EmailField(max_length=240, unique=True)
    stripe_id = models.CharField(max_length=90, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()


class ShippingAddress(models.Model):
    user = models.ForeignKey(Shopper, on_delete=models.CASCADE)
    name = models.CharField(max_length=240)
    address_1 = models.CharField(max_length=1024, help_text="Adresse de voirie et numéro de rue.")
    address_2 = models.CharField(max_length=1024, help_text="Bâtiment, étage, lieu-dit...", blank=True)
    city = models.CharField(max_length=1024)
    zip_code = models.CharField(max_length=32)
    country = models.CharField(max_length=2, choices=[(c.alpha2.lower(), c.name) for c in countries])
