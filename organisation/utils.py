from organisation.models import Branch, BranchBroadcastHistory
from users.models import User, UserProfile

def broadcast_to_branches_by_list(message, branches_list, by, location):
    branch_objs = Branch.objects.filter(id__in = branches_list)
    broadcast_history = BranchBroadcastHistory.objects.create(message = message, broadcast_by = by, broadcast_location=location, organisation = by.organisation)
    broadcast_history.branches.add(*branch_objs)
    
    user_profile_objs = UserProfile.objects.filter(branch__in = branch_objs)
    print("TTTTT ", user_profile_objs)