import random
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from dataclasses import field
from pyexpat import model
from rest_framework import serializers
from users.serializers import ProfileCommentSerializer
from users.models import ProfileComment
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    all_comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_comments(self, obj):
        # Filter and serialize only top-level comments
        top_level_comments_qs = ProfileComment.objects.filter(profile=obj, parent_comment__isnull=True)
        comments_serializer = ProfileCommentSerializer(top_level_comments_qs, many=True)
        return comments_serializer.data

    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_all_comments_count(self, obj):
        # Count all comments for the profile
        return ProfileComment.objects.filter(profile=obj).count()