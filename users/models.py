from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
import uuid
import random
import string
from phonenumber_field.modelfields import PhoneNumberField



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

  def create_superuser(self, user_id, password, **extra_fields):
    user=self._create_user(user_id, password, True, True, **extra_fields)
    user.user_id = user_id
    user.email = 'superadmin@antro.com'
    user.email_verified = True
    user.save()
    return user

def generate_user_id():
    generated_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return generated_id

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=10, unique=True, default=generate_user_id, editable=False)
    email = models.EmailField(max_length=254,null=True, blank=True)
    phone_number = PhoneNumberField(blank=True, null=True)
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
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    verified_by_antro = models.BooleanField(default=False)
    verified_by_user = models.BooleanField(default=False)
    verified_by_organisation = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    onboarding_complete = models.BooleanField(default=True)
    

    USERNAME_FIELD = 'user_id'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    
    # def __str__(self):
    #     return self.user_id
    
    def __str__(self):
        return f"{self.user_id} - {self.email or 'No Email'} - {self.phone_number or 'No Phone Number'}"
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        PhoneVerification.objects.create(user=instance)
        EmailVerification.objects.create(user=instance)
        profile_cat_obj = ProfileCategory.objects.filter(name='Default').first()
        profile_cat_ss_obj = ProfileCategorySocialSite.objects.filter(name="Default", profile_category = profile_cat_obj).first()
        Profile.objects.create(user = instance, category = profile_cat_obj, social_site = profile_cat_ss_obj, email = instance.email if instance.email else None, phone_number = instance.phone_number if instance.phone_number else None, active_profile = True)
    else:
        instance.userprofile.save()

class TempUser(models.Model):
    email = models.EmailField(max_length=254)
    first_name = models.CharField(max_length=254, null=True, blank=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    organisation = models.ForeignKey(
                Organisation, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True
      )
    active = models.BooleanField(default=True)
    onboarding_complete = models.BooleanField(default=True)
    verification_time = models.DateTimeField(null=True, blank=True)
    otp = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        unique_together = ('email', 'organisation',)

class TempUserStatus(models.Model):
    UPLOAD_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('completed', 'Completed'),
    ]
    email = models.EmailField(max_length=254)
    user_id = models.CharField(max_length=10, blank = True, null = True)
    first_name = models.CharField(max_length=254, null=True, blank=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    organisation = models.ForeignKey(
                Organisation, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True
      )
    upload_status = models.CharField(
        max_length=10,
        choices=UPLOAD_STATUS_CHOICES,
        default='Pending'
    )
    failed_reason = models.CharField(max_length=254, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

from profiles.models import Profile,ProfileCategorySocialSite, ProfileCategory        

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
        phone_number = PhoneNumberField(blank=True, null=True)
        image = models.ImageField(upload_to='profile_image', blank=True, null = True)
        gender = models.CharField(default='', blank=True, max_length=20)
        contact_information = models.CharField(null=True, blank= True, max_length=50)
        education = models.CharField(null=True, blank= True, max_length=50)
        experience = models.FloatField(null=True, blank= True)
        designation = models.CharField(null=True, blank= True, max_length=100)
        skills = models.CharField(null=True, blank= True, max_length=1000)
        certifications = models.CharField(null=True, blank= True, max_length=1000)
        awards_recognitions = models.CharField(null=True, blank= True, max_length=1000)
        personal_website = models.CharField(null=True, blank= True, max_length=1000)
        conference_event = models.CharField(null=True, blank= True, max_length=1000)
        languages = models.CharField(null=True, blank= True, max_length=1000)
        projects = models.CharField(null=True, blank= True, max_length=1000)
        active = models.BooleanField(default=True)
        corporate = models.BooleanField(default=False)
        profiles = models.ManyToManyField(Profile, related_name='user_profiles')
        
        def __str__(self):
                return self.user.user_id
        
class TempUserProfile(models.Model):
    user = models.OneToOneField(
            TempUser, 
            on_delete=models.CASCADE, 
            blank=True, 
            null=True, 
            unique=True,
            related_name='tempuserprofile'
    )
    branch = models.ForeignKey(
            Branch, 
            on_delete=models.CASCADE, 
            blank=True, 
            null=True
    )
    bio = models.CharField(max_length=200, default='', blank=True)
    gender = models.CharField(default='', blank=True, max_length=20)
    contact_information = models.CharField(null=True, blank= True, max_length=50)
    education = models.CharField(null=True, blank= True, max_length=50)
    experience =  models.FloatField(null=True, blank= True)
    skills =  models.CharField(null=True, blank= True, max_length=1000)
    certifications = models.CharField(null=True, blank= True, max_length=1000)
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
                return self.user.user_id
        
class EmailVerification(models.Model):
        user = models.OneToOneField(
                User, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True, 
                unique=True,
                related_name='useremailverification'
        )
        verification_time = models.DateTimeField(null=True, blank=True)
        otp = models.IntegerField(null=True, blank=True)
        verified = models.BooleanField(default=False)

        def __str__(self):
                return self.user.user_id
        
class ResetPasswordVerification(models.Model):
        user = models.OneToOneField(
                User, 
                on_delete=models.CASCADE, 
                blank=True, 
                null=True, 
                unique=True,
                related_name='userresetpasswordverification'
        )
        verification_time = models.DateTimeField(null=True, blank=True)
        otp = models.IntegerField(null=True, blank=True)
        updated = models.BooleanField(default=False)

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
    active = models.BooleanField(default=True)
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
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.category.name}"
    
class OnboardingLink(models.Model):
    user = models.ForeignKey(TempUser, on_delete=models.CASCADE)
    android_deeplink_code = models.CharField(max_length=50, null=True, blank=True)
    link_to_email = models.EmailField(max_length=255, null = False, blank=False, verbose_name="Link Email")

    def __str__(self):
        return f"{self.user.email}"
    
class AccountMergeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accountmergerequest')
    from_account = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accountmergerequestfrom')
    verification_time = models.DateTimeField(null=True, blank=True)
    otp = models.IntegerField(null=True, blank=True)
    merged = models.BooleanField(default=False)



class ProfileComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    # Add other fields as needed

class ProfileLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    # Add other fields as needed