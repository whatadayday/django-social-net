from django.db import models
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        try:
            with transaction.atomic():
                user = self.model(email=email, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except Exception as e:
            raise

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=40, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    person_info = models.JSONField(blank=True, null=True)  # Clearbit's data collected for uses

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        return self

    def __unicode__(self):
        return self.email


class Post(models.Model):
    creator = models.ForeignKey(User, blank=True, null=True, related_name="%(class)s_posts", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=60, verbose_name='Title', blank=False, null=False)
    body = models.TextField(max_length=10000, blank=False, null=False)

    like_user_ids = models.JSONField(default=list)  # list of User's id

    def __unicode__(self):
        return u"%s - %s - %s" % (self.creator, self.topic, self.title)

    def created_str(self):
        return format(self.created.strftime('%d.%m.%Y %H:%M'))
