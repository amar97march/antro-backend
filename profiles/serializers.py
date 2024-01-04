import random
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from dataclasses import field
from pyexpat import model
from rest_framework import serializers
from users.serializers import ProfileCommentSerializer
from users.models import ProfileComment, UserProfile
from .models import Profile, ProfileCategory, ProfileCategorySocialSite


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
    
    def to_representation(self, data):
        request = self.context.get("request")
        validated_data = super(ProfileSerializer, self).to_representation(data)
        if request and hasattr(request, "user"):
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.has_profile(data):
                validated_data['saved'] = True
            else:
                validated_data['saved'] = False
        else:
            validated_data['saved'] = False
        if validated_data['image']:
            validated_data['image'] = "https://dev.antrocorp.com" + validated_data['image']
        return validated_data
    
class ProfileCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileCategory
        fields = '__all__'

class ProfileCategorySocialSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileCategorySocialSite
        fields = '__all__'