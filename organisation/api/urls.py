from django.urls import path, re_path

from .views import (
    BroadcastView,
    ParticipantView,
    MyGroup,
    OrganisationMembersView,
    LocationView,
    BranchView,
    GetUsersFormatExcel,
    LocationBranchesView,
    SendBroadcast,
    BranchBroadcastHistoryView,
    UpdatePermissions,
    GroupDetails,
    UpdateGroupMessage,
    FailedUploadMembers)

app_name = 'broadcast'

urlpatterns = [
    path('', BroadcastView.as_view()),
    path('my_groups/', MyGroup.as_view()),
    path('group_details/<str:group_id>', GroupDetails.as_view()),
    path('update_group_message/', UpdateGroupMessage.as_view()),
    path('participant/', ParticipantView.as_view()),
    path('update_permissions/', UpdatePermissions.as_view()),
    path('organisation_members/', OrganisationMembersView.as_view()),
    path('failed_member_uploads/', FailedUploadMembers.as_view()),
    path('locations/', LocationView.as_view()),
    path('location_branches/<str:id>', LocationBranchesView.as_view()),
    path('branch/', BranchView.as_view()),
    path('send_broadcast/', SendBroadcast.as_view()),
    path('get_user_excel/<str:id>/', GetUsersFormatExcel.as_view()),
    path('get_branch_broadcast_history/', BranchBroadcastHistoryView.as_view())
]
