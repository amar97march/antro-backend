from django.contrib.gis.db import models
from users.models import User

class Keyword(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, null=True, blank= True)
    company_name = models.CharField(max_length=100)
    company_sub_heading = models.CharField(max_length=100, null=True, blank= True)
    location = models.PointField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    contact_number_1 = models.CharField(null=True, blank= True, max_length=50)
    contact_number_2 = models.CharField(null=True, blank= True, max_length=50)
    website = models.URLField(null=True, blank= True)
    email = models.EmailField(null=True, blank= True)
    field = models.CharField(max_length=100)
    keywords = models.ManyToManyField(Keyword)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name