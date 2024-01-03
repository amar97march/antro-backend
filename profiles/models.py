from django.contrib.gis.db import models
from django.db.models import Q
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

class ProfileManager(models.Manager):
    def create(self, **kwargs):
        auto_increment_id = 1
        while Profile.objects.filter(antro_id=f"antro-0{auto_increment_id:09}"):
            auto_increment_id += 1
        kwargs["antro_id"] = f"antro-0{auto_increment_id:09}"
        return super().create(**kwargs)
    
    def find_similar_profiles(self, profile):
        # Define the criteria for similarity
        similarity_criteria = (
            Q(category=profile.category) |
            Q(social_site=profile.social_site) |
            # Q(location=profile.location) |
            # Q(address=profile.address) |
            Q(city=profile.city) |
            # Q(contact_number_1=profile.contact_number_1) |
            # Q(contact_number_2=profile.contact_number_2) |
            Q(website=profile.website) |
            Q(profession=profile.profession) |
            Q(keywords__in=profile.keywords.all())
        )

        # Exclude the input profile from the results
        similar_profiles = self.exclude(id=profile.id).filter(similarity_criteria).distinct()

        return similar_profiles

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profileuser')
    antro_id = models.CharField(max_length=20, unique=True, default="")
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    email = models.EmailField(max_length=254, default="", null=True, blank=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    active_profile = models.BooleanField(default = False)
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
    verified_by_antro = models.BooleanField(default=False)
    verified_by_user = models.BooleanField(default=False)
    verified_by_organisation = models.BooleanField(default=False)

    objects = ProfileManager()

    class Meta:
        ordering = ['first_name']

    def __str__(self):
        return self.user.user_id
    
    def find_similar_profiles(self):
        return Profile.objects.find_similar_profiles(self)
    