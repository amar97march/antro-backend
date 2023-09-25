from django.db import models
from django.contrib.auth import get_user_model
from users.models import Organisation

import uuid

User = get_user_model()


GROUP_LEVEL = (
    (0, "Global"),
    (1, "Continent"),
    (2, "Country"),
    (3, "State"),
    (4, "City"),
    (5, "Local"),
)
    

class CompanyBaseModel(models.Model):
     
    organisation = models.ForeignKey(
                Organisation, 
                on_delete=models.CASCADE, 
                blank=False, 
                null=False
      )
    class Meta:
        abstract = True

    # def __str__(self):
    #      return self.organisation.name


class BroadcastMessage(models.Model):
    user = models.ForeignKey(
        User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class Group(CompanyBaseModel):

    class Level(models.TextChoices):
        Global =  0, "Global"
        Continent = 1, "Continent"
        Country = 2, "Country"
        State = 3, "State"
        City = 4, "City"
        Local = 5, "Local"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    participants = models.ManyToManyField(
        User, related_name='broadcast_groups', blank=True)
    messages = models.ManyToManyField(BroadcastMessage, blank=True)
    level = models.CharField(max_length=50,
                              choices=Level.choices,
                              default=Level.Global)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Location(CompanyBaseModel):

    class Level(models.TextChoices):
        Global =  0, "Global"
        Continent = 1, "Continent"
        Country = 2, "Country"
        State = 3, "State"
        City = 4, "City"
        Local = 5, "Local"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    level = models.CharField(max_length=50,
                              choices=Level.choices,
                              default=Level.Global)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name
    
    def get_level_5_objs(self):
        level_5_objs = []

        def traverse_hierarchy(location_obj):
            if location_obj.level == '5':
                level_5_objs.append(location_obj)
                return
            children = Location.objects.filter(parent=location_obj)
            for child in children:
                traverse_hierarchy(child)

        traverse_hierarchy(self)
        return level_5_objs
    

class Branch(CompanyBaseModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank = True)
    branch_name = models.CharField(max_length=100, null=False, blank=False)
    branch_address = models.CharField(max_length=200, null=True, blank=True)
    branch_phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.branch_name


class BranchBroadcastHistory(CompanyBaseModel):

    branches = models.ManyToManyField(
        Branch, related_name='broadcast_history', blank=True)
    message = models.CharField(max_length=1000)
    broadcast_by = models.ForeignKey(User, on_delete=models.CASCADE)
    broadcast_location = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.broadcast_location.name
