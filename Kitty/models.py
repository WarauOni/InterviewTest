from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):  # Added PermissionsMixin
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    date_of_birth = models.DateField(null=True, blank=True)
    picture = models.ImageField(upload_to='user_pictures/', null=True, blank=True)
    no_tel = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    ic_no = models.CharField(max_length=20, unique=True)

    last_login = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Kitty(models.Model):
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    detail = models.TextField()
    history = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField()
    picture = models.ImageField(upload_to='kitty_pictures/', null=True, blank=True)

    def __str__(self):
        return self.name


class Adoption(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Deleting a user deletes their adoption records
        related_name='adoptions'
    )
    kitty = models.ForeignKey(
        Kitty,
        on_delete=models.SET_NULL,  # If a kitty is deleted, the adoption record remains with a NULL kitty
        null=True,
        blank=True,
        related_name='adoptions'
    )
    adopt_id = models.CharField(max_length=20, unique=True)
    adopt_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.kitty:
            return f"{self.user.username} adopting {self.kitty.name}"
        return f"{self.user.username} adoption record (Kitty deleted)"
