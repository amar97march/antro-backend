from django.contrib.gis.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Keyword(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    

class ProfileCategory(models.Model):

    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    def __str__(self):
        return self.name
    
class ProfileCategorySocialSite(models.Model):

    name = models.CharField(max_length=100, null=False, blank=False)
    profile_category = models.ForeignKey(ProfileCategory, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:

        unique_together = ('name', 'profile_category',)

from users.models import User

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    email = models.EmailField(max_length=254, default="", null=True, blank=True)
    phone = PhoneNumberField(blank=True, null=True)
    designation = models.CharField(max_length=100, null=True, blank= True)
    company_name = models.CharField(max_length=100, null = True, blank= True)
    company_sub_heading = models.CharField(max_length=100, null=True, blank= True)
    category = models.ForeignKey(ProfileCategory, on_delete=models.CASCADE)
    category_custom = models.CharField(max_length=100, null=True, blank=True)
    social_site = models.ForeignKey(ProfileCategorySocialSite, on_delete=models.CASCADE)
    social_site_custom = models.CharField(max_length=100, null=True, blank=True)
    location = models.PointField(null=True, default=None)
    address = models.CharField(max_length=100, null = True, blank= True)
    city = models.CharField(max_length=50, null = True, blank= True)
    contact_number_1 = models.CharField(null=True, blank= True, max_length=50)
    contact_number_2 = models.CharField(null=True, blank= True, max_length=50)
    website = models.URLField(null=True, blank= True)
    profession = models.CharField(max_length=100, null = True, blank= True)
    keywords = models.ManyToManyField(Keyword)

    class Meta:
        ordering = ['first_name']

    def __str__(self):
        return self.user.user_id