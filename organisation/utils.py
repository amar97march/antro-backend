from organisation.models import Branch, BranchBroadcastHistory, GroupParticipants, BroadcastMessage, Group
from users.models import User, UserProfile

def broadcast_to_branches_by_list(message, branches_list, by, location):
    branch_objs = Branch.objects.filter(id__in = branches_list)
    broadcast_history = BranchBroadcastHistory.objects.create(message = message, broadcast_by = by, broadcast_location=location, organisation = by.organisation)
    broadcast_history.branches.add(*branch_objs)
    
    user_profile_objs = UserProfile.objects.filter(branch__in = branch_objs)


def is_admin_of_group_or_parent(user, group):
        # Check if the user is an admin of the current group
        if GroupParticipants.objects.filter(group=group, user=user, admin=True).exists():
            print(GroupParticipants.objects.filter(group=group, user=user, admin=True))
            return True

        # If not, check the parent group
        if group.parent:
            return is_admin_of_group_or_parent(user, group.parent)

        return False

def get_messages_of_group_and_children(group_id, message_id):
    try:
        # Find the group based on group_id and combine_id
        group = Group.objects.get(id=group_id)
        broadcast_message_obj = BroadcastMessage.objects.get(id= message_id)

        # Retrieve all child groups recursively
        def get_child_groups(parent_group):
            children = []
            for child_group in Group.objects.filter(parent=parent_group):
                children.append(child_group)
                children.extend(get_child_groups(child_group))
            return children

        child_groups = get_child_groups(group)
        child_groups.append(group)

        # Create a list of group IDs (including the specified group and its children)
        # group_ids = [group.id for group in [group] + child_groups]

        # Get all BroadcastMessage objects associated with these groups
        messages = BroadcastMessage.objects.filter(group__in=child_groups, combine_id=broadcast_message_obj.combine_id)

        return messages

    except Group.DoesNotExist:
        # Handle the case where the group doesn't exist
        return []
    except BroadcastMessage.DoesNotExist:
        # Handle the case where the group doesn't exist
        return []