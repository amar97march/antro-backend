from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from .models import Group, BroadcastMessage

User = get_user_model()


def get_last_10_messages(groupId):
    group = get_object_or_404(Group, id=groupId)
    return group.messages.order_by('-timestamp').all()[:10]

def get_group_details(groupId):
    group = get_object_or_404(Group, id=groupId)
    data = {
        "name": group.name,
        "message_count": group.messages.all().count(),
        "participants": [participant.email for participant in group.participants.all()]
        }
    return data

def get_user_contact(email):
    return get_object_or_404(User, email=email)


def get_current_chat(groupId):
    return get_object_or_404(Group, id=groupId)


def broadcast_to_sub_groups(groupId, message):
    group = Group.objects.get(id = groupId)
    group.messages.add(message)
    group.save()
    child_groups = get_all_sub_groups(group)
    print(child_groups)
    for group_obj in child_groups:
        message_obj = BroadcastMessage.objects.create(
            user=message.user,
            combine_id = message.combine_id,
            content=message.content
        )
        group_obj.messages.add(message_obj)
        group_obj.save()
    


def get_all_sub_groups(group):

    """
    Recursively get all child groups of a parent group.
    """
    child_groups = []
    
    # Get all groups that have the given parent_group as their parent
    direct_child_groups = Group.objects.filter(parent=group)
    
    # Append the direct child groups to the result
    child_groups.extend(direct_child_groups)
    
    # Recursively call the function for each direct child group to get their children
    for child_group in direct_child_groups:
        child_groups.extend(get_all_sub_groups(child_group))
    
    return child_groups