import random
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from dataclasses import field
from pyexpat import model
from rest_framework import serializers
from .models import Card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']