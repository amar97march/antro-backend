from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
import uuid




PROFILE_CATEGORY = (
    ("Social Networking", "Social Networking"),
    ("Video Sharing", "Video Sharing"),
    ("Messaging", "Messaging"),
    ("Event Management", "Event Management"),
    ("Photo Sharing", "Photo Sharing"),
    ("Music Streaming", "Music Streaming"),
    ("Blogging", "Blogging"),
    ("Question and Answer", "Question and Answer"),
    ("Review and Recommendation", "Review and Recommendation"),
    ("Location-Based", "Location-Based"),
    ("Video Conferencing", "Video Conferencing"),
    ("Gaming", "Gaming"),
    ("Ride-Sharing", "Ride-Sharing"),
    ("Dating", "Dating"),
    ("News Aggregation", "News Aggregation"),
    ("File Sharing and Cloud Storage", "File Sharing and Cloud Storage"),
    ("Podcast", "Podcast"),
    ("Payment Gateways", "Payment Gateways"),
    ("Blockchain", "Blockchain"),
    ("Open-Source Development", "Open-Source Development"),
    ("Virtual Reality", "Virtual Reality"),
    ("Augmented Reality", "Augmented Reality"),
    ("Artificial Intelligence", "Artificial Intelligence"),
    ("Other", "Other")
)

class Organisation(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="Company Name")
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True, verbose_name="Company Logo")
    website = models.URLField(max_length=255, blank=True, verbose_name="Website")
    description = models.TextField(blank=True, verbose_name="Description")
    founded_year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Founded Year")
    headquarters = models.CharField(max_length=255, blank=True, verbose_name="Headquarters")
    industry = models.CharField(max_length=255, blank=True, verbose_name="Industry")
    employee_count = models.PositiveIntegerField(null=True, blank=True, verbose_name="Employee Count")
    contact_email = models.EmailField(max_length=255, blank=True, verbose_name="Contact Email")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Phone Number")
    social_media_links = models.JSONField(blank=True, null=True, verbose_name="Social Media Links")
    initial_members_added = models.BooleanField(default=False)

    def __str__(self):
                return self.name

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
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    organisation = models.ForeignKey(
                Organisation, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True
      )
    
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    verified_by_antro = models.BooleanField(default=False)
    verified_by_user = models.BooleanField(default=False)
    verified_by_organisation = models.BooleanField(default=False)
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

from organisation.models import Branch
class UserProfile(models.Model):
        user = models.OneToOneField(
                User, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True, 
                unique=True,
                related_name='userprofile'
        )
        branch = models.ForeignKey(
                Branch, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True
      )
        bio = models.CharField(max_length=200, default='', blank=True)
        phone = models.CharField(blank=True, null=True, max_length=20)
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
        active = models.BooleanField(default=True)
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

from profiles.models import Profile,ProfileCategorySocialSite, ProfileCategory

class AddressBookItem(models.Model):
     
     user = models.ForeignKey(
                User, 
                on_delete=models.CASCADE
      )
     profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
         return self.user.email
     
class DocumentCategory(models.Model):
    name =  models.CharField(max_length=100, blank=False, null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"
     
class Document(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verified_by_antro = models.BooleanField(default=False)
    verified_by_user = models.BooleanField(default=False)
    verified_by_organisation = models.BooleanField(default=False)
    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return f"{self.user.email} - {self.category.name}"