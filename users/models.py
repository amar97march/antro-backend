from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserManager(BaseUserManager):

  def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
    if not email:
        raise ValueError('Users must have an email address')
    now = timezone.now()
    email = self.normalize_email(email)
    user = self.model(
        email=email,
        is_staff=is_staff, 
        is_active=True,
        is_superuser=is_superuser, 
        last_login=now,
        date_joined=now, 
        **extra_fields
    )
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_user(self, email, password, **extra_fields):
    return self._create_user(email, password, False, False, **extra_fields)

  def create_superuser(self, email, password, **extra_fields):
    user=self._create_user(email, password, True, True, **extra_fields)
    return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    
    def __str__(self):
        return self.email
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        PhoneVerification.objects.create(user=instance)
    else:
        instance.userprofile.save()

class UserProfile(models.Model):
        user = models.OneToOneField(
                User, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True, 
                unique=True,
                related_name='userprofile'
        )
        bio = models.CharField(max_length=200, default='', blank=True)
        phone = models.IntegerField(default=0, blank=True)
        image = models.ImageField(upload_to='profile_image', blank=True, null = True)
        gender = models.CharField(default='', blank=True, max_length=20)
        contact_information = models.CharField(null=True, blank= True, max_length=50)
        Education: models.CharField(null=True, blank= True, max_length=50)
        Experience: models.FloatField(null=True, blank= True)
        Skills: models.CharField(null=True, blank= True, max_length=1000)
        Certifications: models.CharField(null=True, blank= True, max_length=1000)
        awards_recognitions = models.CharField(null=True, blank= True, max_length=1000)
        personal_website = models.CharField(null=True, blank= True, max_length=1000)
        conference_event = models.CharField(null=True, blank= True, max_length=1000)
        languages = models.CharField(null=True, blank= True, max_length=1000)
        projects = models.CharField(null=True, blank= True, max_length=1000)
        def __str__(self):
                return self.user.email
        
class PhoneVerification(models.Model):
        user = models.OneToOneField(
                User, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True, 
                unique=True,
                related_name='userphoneverification'
        )
        verification_time = models.DateTimeField(null=True, blank=True)
        otp = models.IntegerField(null=True, blank=True)
        verified = models.BooleanField(default=False)

        def __str__(self):
                return self.user.email
        
class RequestData(models.Model):
     
     user = models.ForeignKey(
                User, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True
      )
     data = models.JSONField(default = dict)
     request_id = models.UUIDField(primary_key = True)
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
         return self.user.email