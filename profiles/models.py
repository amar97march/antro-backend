from django.contrib.gis.db import models


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
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, default="")
    phone = models.CharField(max_length=20, default="")
    designation = models.CharField(max_length=100, null=True, blank= True)
    company_name = models.CharField(max_length=100)
    company_sub_heading = models.CharField(max_length=100, null=True, blank= True)
    category = models.ForeignKey(ProfileCategory, on_delete=models.CASCADE)
    category_custom = models.CharField(max_length=100, null=True, blank=True)
    social_site = models.ForeignKey(ProfileCategorySocialSite, on_delete=models.CASCADE)
    social_site_custom = models.CharField(max_length=100, null=True, blank=True)
    location = models.PointField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    contact_number_1 = models.CharField(null=True, blank= True, max_length=50)
    contact_number_2 = models.CharField(null=True, blank= True, max_length=50)
    website = models.URLField(null=True, blank= True)
    profession = models.CharField(max_length=100)
    keywords = models.ManyToManyField(Keyword)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name