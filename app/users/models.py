import math
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

ELO_START_VALUE = 400
ELO_FACTOR_K = 20

class UserManager(BaseUserManager):
    ''' Manager for user model '''
    def create_user(self, username, password=None, **extra_fields):
        ''' create save and return new user '''
        if not username:
            raise ValueError('need to provide username.')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        ''' create save and return new superuser '''
        user = self.create_user(username, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()



class User(AbstractBaseUser, PermissionsMixin):
    ''' User model in system '''
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=255, blank=True, null=True, default=None, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    elo_rating = models.FloatField(default=ELO_START_VALUE)

    def probability(self, opponent):
        return 1 / (1 + math.pow(10, (opponent.elo_rating - self.elo_rating) / 400))

    def updated_elo(self, opponent, result):
        return round(self.elo_rating + ELO_FACTOR_K * (result - self.probability(opponent)), 1)

    objects = UserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'


