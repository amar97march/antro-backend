from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt import views as jwt_views
from .views import *

app_name = 'users'

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('get_user_data/<str:id>/', UserDataById.as_view(), name='user_data_by_id'),
    path('get_user_data/', UserData.as_view(), name='user_data'),
    path('create_organisation/', OrgansationView.as_view(), name="organisation_view"),
    path('create_members/', CreateMembersView.as_view(), name="create_members_view"),
    path('d_link_secret_details/<str:secret>/', DLinkSecretDetails.as_view(), name="d_link_secret_details"),
    path('create_members_history/', CreateMembersHistoryView.as_view(), name="create_members_hisotry_view"),
    path('get_token_by_phone_otp/', GetTokenByPhoneOTP.as_view(), name="get_token_by_phone_otp"),
    path('check_otp/', CheckOtp.as_view(), name="checkOtp"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('resend-otp/', ResendOTP.as_view(), name='register'),
    path('send-otp/', SendOTP.as_view(), name='register'),
    path('verify-account-otp/', VerifyOTP.as_view(), name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='register'),
    path('reset-password-request/', ResetPasswordRequest.as_view(), name='reset-password-request'),
    path('token-refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('get_data/<str:id>/', GetData.as_view(), name='get_data'),
    path('address_book/', AddressBook.as_view(), name='address_book'),
    path('add_address_book_profile/', AddAddressBookProfile.as_view(), name='add_address_book_profile'),
    path('documents/', DocumentList.as_view(), name='document-list'),
    path('document_upload/', DocumentUpload.as_view(), name="Document Upload"),
    path('add_user_profile_picture/', AddUserProfilePicture.as_view(), name="profile-picture"),
    path('document_delete/<int:document_id>/', DocumentDelete.as_view(), name="Document Upload"),
    path('document_categories/', DocumentCategoryView.as_view(), name="document categories"),
    path('deactivate-user/', DeactivateUserView.as_view(), name='deactivate-user'),
    path('get-user-by-secret/<str:secret>/', GetUserBySecret.as_view(), name='get-user-by-secret'),
    path('add-user-by-secret/', AddUserBySecret.as_view(), name='add-user-by-secret'),
    path('search_users/<str:keyword>/', SearchUsers.as_view(), name='search_users'),
    path('merge_account/', MergeAccount.as_view(), name='merge-account'),
    path('profile_comments/', ProfileCommentListCreateView.as_view(), name='comment-list-create'),
    path('profile_comments/<int:pk>/', ProfileCommentRetrieveUpdateDestroyView.as_view(), name='comment-retrieve-update-destroy'),
    path('profile_likes/', ProfileLikeCreateView.as_view(), name='like-create'),
    path('profile_likes/<int:pk>/', ProfileLikeDestroyView.as_view(), name='like-destroy'),
    path('smart_find_user/', SmartFindUser.as_view(), name='smart-find-user'),
    path('create_authentication_entity/', CreateAuthenticationEntity.as_view(), name='create-authentication-entity'),
    path('authentication-entity-status/<str:authentication_entity_id>/', CheckAuthenticationEntity.as_view(), name='authentication-entity-update'),
    path('data_exist_check/', DataExistCheck.as_view(), name='data_exist_check'),
    path('create_user_from_auth_entity/', CreateUserFromAuthEntity.as_view(), name='create_user_from_auth_entity'),
    path('send_email_phone_otp/', SendEmailPhoneOtp.as_view(), name='send_email_phone_otp'),
]
