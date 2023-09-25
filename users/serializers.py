from rest_framework import serializers
from .models import User, UserProfile, AddressBookItem, Organisation

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','email', 'first_name', 'last_name', 'date_of_birth']
        read_only_fields = ['email', 'id']

    def create(self, validated_data):
        print(validated_data)
        return User.objects.create(**validated_data)

class UserProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = '__all__'

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

class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'date_of_birth', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(email=self.validated_data['email'], date_of_birth=self.validated_data['date_of_birth'])
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value
    
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
    
class OrganisationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organisation
        fields = ['id', 'name', 'logo', 'website', 'description', 'founded_year', 'headquarters', 'industry', 'employee_count','contact_email', 'phone_number', 'initial_members_added']
        read_only_fields = ['id']

    def create(self, validated_data):

        return Organisation.objects.create(**validated_data)

    def to_representation(self, data):
        
        data = super(OrganisationSerializer, self).to_representation(data)
        data["logo"] = "http://localhost:8000"+ data["logo"]
        return data