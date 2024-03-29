from rest_framework import serializers
from .models import User, UserProfile, AddressBookItem, Organisation, DocumentCategory, Document, OnboardingLink,\
EmailVerification, PhoneVerification, TempUser, ProfileComment, ProfileLike, TempUserStatus
from organisation.models import Branch
import random
from users.utils import send_email_verification_otp, send_verification_otp, generate_random_string
from datetime import datetime, timedelta
import re
import secrets
import string
from phonenumber_field.phonenumber import PhoneNumber


class HiddenUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'phone_number', 'first_name', 'last_name']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Hide middle numbers of phone_number
        if representation.get('phone_number'):
            phone_number = representation['phone_number']
            hidden_phone_number = f'{phone_number[:4]}XXXXXXX{phone_number[-2:]}'
            representation['phone_number'] = hidden_phone_number

        # Hide most of the email
        if representation.get('email'):
            email = representation['email']
            username, domain = email.split('@')
            hidden_email = f'{username[:3]}XXX@{domain}'
            representation['email'] = hidden_email

        return representation


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'user_id','email', 'phone_number', 'first_name', 'last_name', 'date_of_birth', 'onboarding_complete', 'is_staff', 'email_verified', 'phone_verified']
        read_only_fields = ['email', 'id']

    def create(self, validated_data):
        return User.objects.create(**validated_data)
    
class TempUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = TempUser
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'onboarding_complete']
        read_only_fields = ['email', 'id']

class TempUserStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = TempUserStatus
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'onboarding_complete']
        read_only_fields = ['email', 'id']

class UserProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['phone_number']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    
    
    def to_representation(self, instance):
        data = super(UserProfileSerializer, self).to_representation(instance)
        # representation["user"] = instance.user.email
        if (instance.branch):
            branch_obj = Branch.objects.filter(id = instance.branch.id).first()
            if branch_obj:
                data["branch"] = branch_obj.branch_name
            else:
                data["branch"] = None
        else:
                data["branch"] = None
        print(data, 'AA')
        if data["image"]:
            data['image'] = "http://dev.antrocorp.com" + str(data["image"])
        return data
    

def detect_email_or_phone(input_str):
    # Check if the input is an email address
    email_pattern = re.compile(r'^\S+@\S+\.\S+$')
    if email_pattern.match(input_str):
        return 'email'

    # Check if the input is a phone number
    try:
        phone_number = PhoneNumber.from_string(input_str)
        return 'phone'
    except Exception:
        pass

    return None

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255, required=False)
    phone_number = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True, required=False)
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'date_of_birth', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        # Check if the input is an email address
        email_pattern = re.compile(r'^\S+@\S+\.\S+$')
        if 'email' in self.validated_data:
            email = self.validated_data['email']
            pattern = r'^\S+@\S+\.\S+$'
    
    # Use re.match() to search for the pattern at the beginning of the string
            match = re.match(pattern, email)
            if not match:
                raise serializers.ValidationError("Invalid email")
            user_obj = User.objects.filter(email = email, email_verified = True).first()
            if user_obj:
                raise serializers.ValidationError("Email already in use.")
            else:
                user_obj = User.objects.filter(email = email).first()
                
                if user_obj:
                    user_obj.date_of_birth = self.validated_data['date_of_birth']
                    user_obj.first_name = self.validated_data['first_name']
                    user_obj.last_name = self.validated_data['last_name']
                    user_obj.save()
                else:
                    user_obj = User(email=email,
                                date_of_birth=self.validated_data['date_of_birth'],
                                first_name = self.validated_data['first_name'],
                                last_name = self.validated_data['last_name']
                            )
                password = self.validated_data['password']
                password2 = self.validated_data['password2']
                if password != password2:
                    raise serializers.ValidationError({'password': 'Passwords must match.'})
                user_obj.set_password(password)
                user_obj.save()
                email_obj, flag = EmailVerification.objects.get_or_create(user = user_obj)
                email_obj.otp = random.randint(1000, 9999)
                email_obj.verification_time = datetime.now() + timedelta(minutes=2)
                email_obj.save()
                send_email_verification_otp(user_obj.email, email_obj.otp)
        elif 'phone_number' in self.validated_data:
            user_obj = User.objects.filter(phone_number = self.validated_data['phone_number'], phone_verified = True).first()
            if not user_obj:
                user_obj = User.objects.filter(phone_number = self.validated_data['phone_number']).first()
                if not user_obj:
                    user_obj = User(phone_number=self.validated_data['phone_number']
                            )
                    user_obj.set_password(generate_random_string())
                    user_obj.save()
            phone_verification_obj, flag = PhoneVerification.objects.get_or_create(user = user_obj)
            phone_verification_obj.otp = 1234 #random.randint(1000, 9999)
            phone_verification_obj.verification_time = datetime.now() + timedelta(minutes=2)
            phone_verification_obj.verified = False
            phone_verification_obj.save()
            send_verification_otp(user_obj.phone_number, phone_verification_obj.otp)
        
        else:
            raise serializers.ValidationError("Invalid Email or Phone Number")

        # input_type = detect_email_or_phone(self.validated_data['email'])
        
        return user_obj


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value
    
    
class OrganisationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organisation
        fields = ['id', 'name', 'logo', 'website', 'description', 'founded_year', 'headquarters', 'industry', 'employee_count','contact_email', 'phone_number', 'initial_members_added']
        read_only_fields = ['id']

    def create(self, validated_data):

        return Organisation.objects.create(**validated_data)

    def to_representation(self, data):
        
        data = super(OrganisationSerializer, self).to_representation(data)
        data["logo"] = "http://dev.antrocorp.com"+ data["logo"]
        return data
    

class DocumentCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentCategory
        fields = ('id', 'created_at', 'name') 

class DocumentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    file_size = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()

    def get_file_size(self, obj):
        if obj.file:
            return obj.file.size
        return None

    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]  # Extract the file name from the full path
        return None
    
    def get_file_extension(self, obj):
        if obj.file:
            return obj.file.name.split('.')[-1]  # Extract the file extension from the file name
        return None
    
    class Meta:
        model = Document
        fields = ('category_name', 'id', 'created_at', 'category', 'user', 'verified_by_antro', 'verified_by_user', 'verified_by_organisation', 'file', 'file_size', 'file_name', 'file_extension')

class OnboardingLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingLink
        fields = ('secret',)



class ProfileCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = ProfileComment
        fields = '__all__'
        read_only_fields = ['user']

    def get_replies(self, obj):
        # Recursively serialize replies
        replies_qs = ProfileComment.objects.filter(parent_comment=obj)
        replies_serializer = ProfileCommentSerializer(replies_qs, many=True)
        return replies_serializer.data

class ProfileLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileLike
        fields = '__all__'
        read_only_fields = ['user']

from profiles.serializers import ProfileSerializer
class AddressBookItemSerializer(serializers.Serializer):

    class Meta:
        model = AddressBookItem
        fields = ''

    def to_representation(self, instance):
        representation = dict()
        representation["user"] = instance.user.email
        representation["profile"] = ProfileSerializer(instance.profile).data 
        return representation
    
class TempUserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempUserStatus
        fields = '__all__'

class DetailUserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(required=False, source='userprofile')
    profiles = ProfileSerializer(many=True, required=True, source='profileuser')

    class Meta:
        model = User
        fields = ("user_id", "email", "phone_number", "first_name", "last_name", "date_of_birth", "organisation", "is_staff", "is_admin", "is_active", "active", "email_verified", "phone_verified", "verified_by_antro", "verified_by_user", "verified_by_organisation", "last_login", "date_joined", "onboarding_complete", "user_profile","profiles")
