from rest_framework import serializers
from chat.views import get_user_contact
from users.models import User
from users.serializers import UserSerializer

from organisation.models import Group, Location, Branch, BranchBroadcastHistory

class GroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'level', 'parent', 'created_at', 'participants']

    def create(self, validated_data):
        print(validated_data)
        request = self.context.get("request")
        participants = validated_data.pop('participants')
        if request and hasattr(request, "user"):
            validated_data["organisation"] = request.user.organisation
        group = Group.objects.create(**validated_data)
        for user_id in participants:
            group.participants.add(user_id)
        group.save()
        
        return group
    
    def to_representation(self, data):
        data = super(GroupSerializer, self).to_representation(data)
        data['member_count'] = len(data['participants'])
        data["participants"] =  [User.objects.get(id=id).email for id in data['participants']]
        print(data)
        return data

class BranchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Branch
        fields = ['id', 'location', 'branch_name', 'branch_address', 'branch_phone', 'created_at']

    def create(self, validated_data):
        # print(validated_data)
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["organisation"] = request.user.organisation
        branch_obj = Branch.objects.create(**validated_data)
        # for user_id in members:
        #     location_obj.members.add(user_id)
        branch_obj.save()
        
        return branch_obj



class LocationSerializer(serializers.ModelSerializer):
    sublocations = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'level', 'parent', 'created_at', 'sublocations']

    def create(self, validated_data):
        print(validated_data)
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["organisation"] = request.user.organisation
        location_obj = Location.objects.create(**validated_data)
        # for user_id in members:
        #     location_obj.members.add(user_id)
        location_obj.save()
        
        return location_obj
    
    def get_sublocations(self, obj):
        # Recursively serialize child locations
        sublocations = Location.objects.filter(parent=obj)
        serializer = LocationSerializer(sublocations, many=True)
        return serializer.data
    
    def to_representation(self, data):
        data = super(LocationSerializer, self).to_representation(data)
        if data['level'] == '5':
            print("AFAFAFA ", data['level'])
            branched_list = Branch.objects.filter(location__id = data['id'])
            data['branches'] = BranchSerializer(branched_list, many=True).data
            
        
        # data['member_count'] = len(data['participants'])
        # data["participants"] =  [User.objects.get(id=id).email for id in data['participants']]
        # print(data)
        return data


class BranchBroadcastHistorySerializer(serializers.ModelSerializer):

    branches = BranchSerializer(many=True, read_only=True, source='branches.all')
    broadcast_location = serializers.CharField(source='broadcast_location.name', read_only=True)
    broadcast_by = serializers.CharField(source='broadcast_by.email', read_only=True) 
    
    class Meta:
        model = BranchBroadcastHistory
        fields = '__all__'

    

