from rest_framework import serializers
from chat.views import get_user_contact
from users.models import User
from users.serializers import UserSerializer
from organisation.utils import is_admin_of_group_or_parent

from organisation.models import Group, Location, Branch, BranchBroadcastHistory, GroupParticipants


class GroupParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupParticipants
        fields = ['user', 'group', 'sender','admin', 'joined_at']

class GroupSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),  # Queryset for the User model
        many=True,  # Set to True for a ManyToManyField
        required=False  # Set to True if the field is required
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'level', 'parent', 'created_at', 'participants']

    def create(self, validated_data):
        print(type(validated_data))
        request = self.context.get("request")
        # print(validated_data["participants"])
        participants = validated_data.pop('participants')
        # print("PP", participants)
        # del validated_data['participants']
        if request and hasattr(request, "user"):
            validated_data["organisation"] = request.user.organisation
        group = Group.objects.create(**validated_data)
        for user_id in participants:
            # print("KAKAK", user_id)
            # user_obj = User.objects.get(id = user_id)
            # group_participant = GroupParticipants(group=group, user=user_obj)
            # group_participant.save()
            group.participants.add(user_id)
        group.save()
        group_participant_obj = GroupParticipants.objects.get(group = group, user = request.user)
        group_participant_obj.sender = True
        group_participant_obj.admin = True
        group_participant_obj.save()

        
        return group
    
    # def get_members(self, obj):
    #     # Get the GroupParticipants instances related to this group
    #     group_participants = GroupParticipants.objects.filter(group=obj)
    #     return GroupParticipantsSerializer(group_participants, many=True).data
    
    def to_representation(self, data):
        request = self.context.get("request")
        validated_data = super(GroupSerializer, self).to_representation(data)
        # Include data from GroupParticipants for each group
        if 'participants' in validated_data:
            group_participants_data = []
            for user in validated_data['participants']:
                # Assuming you have a relationship between User and GroupParticipants
                group_participant = GroupParticipants.objects.filter(user=user, group=validated_data['id']).first()
                if group_participant:
                    participant_data = {
                        'id': user,
                        'email': group_participant.user.email,
                        'sender': group_participant.sender,
                        'admin': group_participant.admin,
                        'joined_at': group_participant.joined_at,
                    }
                    group_participants_data.append(participant_data)

            validated_data['participants'] = group_participants_data
            validated_data['member_count'] = len(group_participants_data)
            group_participant = GroupParticipants.objects.filter(user=request.user, group=validated_data['id']).first()
            if group_participant:
                validated_data['is_sender'] = group_participant.sender
            else:
                validated_data['is_sender'] = False
            validated_data['has_admin_access'] = is_admin_of_group_or_parent(request.user, data)
            validated_data['parent_hierarchy'] = data.parent_hierarchy_as_json()

        return validated_data

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

    

