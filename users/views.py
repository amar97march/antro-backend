from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import status, generics, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import  Response
from rest_framework.views import APIView
from .utils import get_tokens_for_user, compare_selfie_with_all_users
from django.db.models import Q
from rest_framework_simplejwt.tokens import OutstandingToken
from users.models import User, PhoneVerification, UserProfile, RequestData, AddressBookItem,\
Document, DocumentCategory, OnboardingLink, EmailVerification, ResetPasswordVerification, TempUser , TempUserProfile, AccountMergeRequest,\
ProfileComment, ProfileLike, TempUserStatus, AuthenticationEntity, HandGesture
from .serializers import RegistrationSerializer, PasswordChangeSerializer, UserSerializer, UserProfileSerializer, \
AddressBookItemSerializer, OrganisationSerializer, DocumentSerializer, DocumentCategorySerializer, HiddenUserSerializer,\
ProfileCommentSerializer, ProfileLikeSerializer, TempUserStatusSerializer, DetailUserSerializer
from .utils import send_verification_otp, send_reset_password_otp, send_email_verification_otp, send_email_account_merge_otp
from .tasks import perform_user_detection, test
from django.shortcuts import get_object_or_404
from django.utils.timezone import utc
from django.conf import settings
import json
from django.utils import timezone
import random
import datetime
import uuid
from profiles.models import Profile
from organisation.models import Group, Branch, Location
# from push_notifications.models import WebPushDevice
import re
from users.utils import send_notification, generate_random_string
from phonenumber_field.phonenumber import PhoneNumber

from django.db.models import Count, DateField, F
from django.db.models.functions import TruncDate
from django.core.files.storage import default_storage
from moviepy.editor import VideoFileClip


class RegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user_obj = serializer.save()
            email = request.data.get('email')
            # input_type = detect_email_or_phone(request.data.get('email'))
            if email:
                user_profile_obj = UserProfile.objects.get(user = user_obj)
                user_profile_obj.designation = request.data.get('designation')
                user_profile_obj.save()
                profile_obj = Profile.objects.get(user = user_obj)
                profile_obj.name = user_obj.first_name + " " + user_obj.last_name
                profile_obj.designation = request.data.get('designation')
                profile_obj.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserData(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            user_obj = User.objects.get(id = request.user.id)
            organisation_serializer_obj = OrganisationSerializer(user_obj.organisation)
            data = {
                "id": user_obj.id,
                "first_name": user_obj.first_name,
                "last_name": user_obj.last_name,
                "email": user_obj.email,
                "dob": user_obj.date_of_birth,
                "is_staff": user_obj.is_staff,
                "user_data": {"organisation": organisation_serializer_obj.data,
                                      "email": user_obj.email,
                                      "first_name": user_obj.first_name,
                                      "last_name": user_obj.last_name,
                                      }
            }
            return Response({'response_data': data}, status=status.HTTP_200_OK)
           
        except Exception as e:
            print(e)
            return Response({'request_id':id, 'response_data': 'Invalid request id'}, status=status.HTTP_400_BAD_REQUEST)


class UserDataById(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, id):

        try:
            user_obj = User.objects.get(id = request.user.id)
            # organisation_serializer_obj = OrganisationSerializer(user_obj.organisation)
            data_user_obj = User.objects.get(user_id = id)

            if (data_user_obj.organisation == user_obj.organisation):
                user_data = DetailUserSerializer(data_user_obj)
                return Response({'response_data': user_data.data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Not permitted'}, status=status.HTTP_400_BAD_REQUEST)

           
        except Exception as e:
            print(e)
            return Response({'request_id':id, 'response_data': 'Invalid request id'}, status=status.HTTP_400_BAD_REQUEST)

      
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        
       
        # input_type = detect_email_or_phone(request.data.get('email'))
        # request.data.get('email')
        email = request.data.get('email')
        print("aa", email)
        if email:
            if 'email' not in request.data or 'password' not in request.data:
                return Response({'data': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
            email = request.data.get('email')
            password = request.data.get('password')
            user_obj = User.objects.filter(email = request.data.get('email'), email_verified = True).first()
            print("afasf1", email, password)
            if not user_obj:
                 return Response({'data': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            print("fss", user_obj.user_id)
            user = authenticate(request, username=user_obj.user_id, password=password)
            print("user: ", user)
            if user is not None:
                if not user.active:
                    print("afasf2")
                    return Response({'data': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
                # phone_obj = PhoneVerification.objects.get(user = user)
                email_obj = EmailVerification.objects.get(user = user)
                if(not email_obj.verified):
                    return Response({'data': 'Email not verified'}, status=status.HTTP_401_UNAUTHORIZED)
                login(request, user)
                auth_data = get_tokens_for_user(request.user)
                # auth_data["verified"] = email_obj.verified
                auth_data["is_staff"] = user.is_staff
                organisation_serializer_obj = OrganisationSerializer(user.organisation)
                auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                        "email": email,
                                        "first_name": user.first_name,
                                        "last_name": user.last_name,
                                        "id": user.id
                                        }
                return Response({'data': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
            print('asf', user)
        elif request.data.get('phone_number'):
            user_obj = User.objects.filter(phone_number = request.data.get('phone_number'), phone_verified = True).first()
            if not user_obj:
                user_obj = User.objects.filter(phone_number = request.data.get('phone_number')).first()
                if not user_obj:
                    user_obj = User(phone_number=request.data.get('phone_number')
                            )
                    user_obj.set_password(generate_random_string())
                    user_obj.save()
            phone_verification_obj, flag = PhoneVerification.objects.get_or_create(user = user_obj)
            phone_verification_obj.otp = random.randint(1000, 9999)
            phone_verification_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
            phone_verification_obj.verified = False
            phone_verification_obj.save()
            send_verification_otp(user_obj.phone_number, phone_verification_obj.otp)
            return Response({'data': 'OTP Sent'}, status=status.HTTP_200_OK)
        else:
            print("asf33")
            return Response({'data': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            # user = authenticate(request, email=email, password=password)
        print("asf23")
        return Response({'data': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class SendOTP(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user:
            return Response({'data': 'Invalid account missing'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = request.user
        country_code = request.data.get('country_code')
        phone_number = request.data.get('phone_number')
        otp = send_verification_otp(f'+{country_code}{phone_number}')
        if otp:

            phone_obj = PhoneVerification.objects.get(user = user)
            phone_obj.otp = otp
            phone_obj.verification_time = datetime.datetime.now()
            phone_obj.save()
            return Response({'data': 'Otp send successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'data': 'OTP not send. Please try after sometime'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get('otp')
        verification_type = request.data.get('type')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        new_password = request.data.get('new_password')

        try:
            # user = User.objects.get(email = email)
            if (verification_type == "phone"):
                user = User.objects.get(phone_number = phone_number, phone_verified = False)
                phone_obj = PhoneVerification.objects.get(user = user)
                if phone_obj.otp == otp and (((datetime.datetime.utcnow().replace(tzinfo=utc) -  phone_obj.verification_time).total_seconds()/60) < 30) :
                    phone_obj.verified = True
                    phone_obj.save()
                    user.phone_verified = True
                    user.save()
                    auth_data = get_tokens_for_user(user)
                    auth_data["is_staff"] = user.is_staff
                    organisation_serializer_obj = OrganisationSerializer(user.organisation)
                    auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                            "email": user.email,
                                            "phone_number": str(user.phone_number),
                                            "first_name": user.first_name,
                                            "last_name": user.last_name,
                                            "id": user.id
                                            }
                    return Response({'data': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
                    # return Response({'data': 'Account verified'}, status=status.HTTP_200_OK)
                else:
                    return Response({'data': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            elif (verification_type == "email"):
                user = User.objects.get(email = email)
                email_obj = EmailVerification.objects.get(user = user, verified = False)
                if email_obj.verification_time > datetime.datetime.utcnow().replace(tzinfo=utc) and email_obj.otp == int(otp):
                    email_obj.verified = True
                    email_obj.otp = None
                    email_obj.save()
                    user.email_verified = True
                    user.save()
                    auth_data = get_tokens_for_user(user)
                    auth_data["is_staff"] = user.is_staff
                    organisation_serializer_obj = OrganisationSerializer(user.organisation)
                    auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                            "email": user.email,
                                            "phone_number": str(user.phone_number),
                                            "first_name": user.first_name,
                                            "last_name": user.last_name,
                                            "id": user.id
                                            }
                    TempUserStatus.objects.create(first_name = user.first_name,
                                                   last_name = user.last_name,
                                                   email = user.email,
                                                   organisation = user.organisation,
                                                   date_of_birth = user.date_of_birth,
                                                   phone_number = user.phone_number,
                                                   upload_status = 'completed'
                                                   )
                    auth_data = get_tokens_for_user(user)
                    auth_data["is_staff"] = user.is_staff
                    organisation_serializer_obj = OrganisationSerializer(user.organisation)
                    auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                            "email": user.email,
                                            "phone_number": str(user.phone_number),
                                            "first_name": user.first_name,
                                            "last_name": user.last_name,
                                            "id": user.id
                                            }
                    return Response({'data': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
                    # return Response({'data': auth_data}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid or expired otp'}, status=status.HTTP_400_BAD_REQUEST)
            elif (verification_type == "reset_password"):
                temp_user_obj = TempUser.objects.filter(email = email).first()
                if temp_user_obj:
                    if temp_user_obj.verification_time > datetime.datetime.utcnow().replace(tzinfo=utc) and temp_user_obj.otp == int(otp):
                        temp_user_obj.onboarding_complete = True
                        temp_user_obj.otp = None

                        
                        onboarding_obj = OnboardingLink.objects.filter(user=temp_user_obj).first()
                        onboarding_obj.android_deeplink_code = None
                        onboarding_obj.save()
                        user = User.objects.create(email = temp_user_obj.email,
                                                   first_name = temp_user_obj.first_name,
                                                   last_name = temp_user_obj.last_name,
                                                   phone_number = temp_user_obj.phone_number,
                                                   date_of_birth = temp_user_obj.date_of_birth,
                                                   organisation = temp_user_obj.organisation
                                                   )
                        temp_user_profile_obj = TempUserProfile.objects.filter(user = temp_user_obj).first()
                        user_profile_obj = UserProfile.objects.filter(user = user).first()
                        user_profile_obj.branch = temp_user_profile_obj.branch
                        user_profile_obj.bio = temp_user_profile_obj.bio
                        user_profile_obj.gender = temp_user_profile_obj.gender
                        user_profile_obj.contact_information = temp_user_profile_obj.contact_information
                        user_profile_obj.education = temp_user_profile_obj.education
                        user_profile_obj.experience = temp_user_profile_obj.experience
                        user_profile_obj.skills = temp_user_profile_obj.skills
                        user_profile_obj.certifications = temp_user_profile_obj.certifications
                        user_profile_obj.awards_recognitions = temp_user_profile_obj.awards_recognitions
                        user_profile_obj.personal_website = temp_user_profile_obj.personal_website
                        user_profile_obj.conference_event = temp_user_profile_obj.conference_event
                        user_profile_obj.languages = temp_user_profile_obj.languages
                        user_profile_obj.projects = temp_user_profile_obj.projects
                        user_profile_obj.corporate = True
                        user_profile_obj.save()
                        temp_user_profile_obj.active = False
                        temp_user_profile_obj.save()
                        temp_user_obj.active = False
                        temp_user_obj.save()
                        temp_user_status = TempUserStatus.objects.filter(email = user.email).first()
                        temp_user_status.upload_status = 'completed'
                        temp_user_status.user_id = user.user_id
                        temp_user_status.save()
                        user.set_password(new_password)
                        user.save()
                        auth_data = get_tokens_for_user(user)
                        auth_data["is_staff"] = user.is_staff
                        organisation_serializer_obj = OrganisationSerializer(user.organisation)
                        auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                                "email": user.email,
                                                "phone_number": str(user.phone_number),
                                                "first_name": user.first_name,
                                                "last_name": user.last_name,
                                                "id": user.id
                                                }
                        return Response({'data': 'Password resetted', **auth_data}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invalid or expired otp'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    user = User.objects.get(email = email)
                    reset_password_obj = ResetPasswordVerification.objects.get(user = user)
                    if reset_password_obj.verification_time > datetime.datetime.utcnow().replace(tzinfo=utc) and reset_password_obj.otp == int(otp):
                        reset_password_obj.updated = True
                        reset_password_obj.otp = None
                        reset_password_obj.save()
                        user.set_password(new_password)
                        user.save()
                        auth_data = get_tokens_for_user(user)
                        auth_data["is_staff"] = user.is_staff
                        organisation_serializer_obj = OrganisationSerializer(user.organisation)
                        auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                                "email": user.email,
                                                "phone_number": str(user.phone_number),
                                                "first_name": user.first_name,
                                                "last_name": user.last_name,
                                                "id": user.id
                                                }
                        return Response({'data': 'Password resetted', **auth_data}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invalid or expired otp'}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                return Response({'error': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error': 'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ResendOTP(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        # otp = request.data.get('otp')
        verification_type = request.data.get('type')
        email = request.data.get('email')

        try:
            user = User.objects.get(email = email)
            if (verification_type == "email_verification"):

                email_obj = EmailVerification.objects.get(user = user)
                email_obj.otp = random.randint(1000, 9999)
                email_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
                email_obj.save()
                send_email_verification_otp(user.email, email_obj.otp)
                return Response({'data': 'Otp sent'}, status=status.HTTP_200_OK)
                
            else:
                return Response({'error': 'Invalid type'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'error': 'Invalid Request'}, status=status.HTTP_400_BAD_REQUEST)
        

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'data': 'Successfully Logged out'}, status=status.HTTP_200_OK)

      
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = PasswordChangeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True) #Another way to write is as in Line 17
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ResetPasswordRequest(APIView):

    permission_classes = [AllowAny, ]

    def post(self, request):
        email = request.data.get('email')
        try:
            user_obj = User.objects.get(email = email)
            reset_obj, created = ResetPasswordVerification.objects.get_or_create(user = user_obj)
            reset_obj.otp = random.randint(1000, 9999)
            reset_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
            send_reset_password_otp(user_obj.email, reset_obj.otp)
            reset_obj.updated = False
            reset_obj.save()
            return Response({'data': 'Reset OTP sent'}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'request_id':id, 'response_data': 'Invalid request id'}, status=status.HTTP_400_BAD_REQUEST)
        


class GetData(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request, id):
        try:
            obj = RequestData.objects.get(request_id=id)
            if obj.user == request.user:
                return Response({'request_id':id ,'response_data': obj.data}, status=status.HTTP_200_OK)
            else:
                return Response({'request_id':id, 'response_data': 'Invalid request id'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'request_id':id, 'response_data': 'Invalid request id'}, status=status.HTTP_400_BAD_REQUEST)
        


class UserProfileView(APIView):

    permission_classes = [IsAuthenticated, ]
    def get(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from profiles.models import ProfileCategory, ProfileCategorySocialSite

class AddressBook(APIView):

    permission_classes = [IsAuthenticated, ]

    def get(self, request):

        try:
            data = {}

            for cat in ProfileCategory.objects.all():

                address_book_items = AddressBookItem.objects.filter(user = request.user,profile__category = cat)
                if (address_book_items):
                    serializer = AddressBookItemSerializer(address_book_items, many = True)
                    data[cat.name] = serializer.data

            return Response({'data': data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({'error': 'Error fetching '+ str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AddAddressBookProfile(APIView):

    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:

            profile_obj = Profile.objects.get(id = request.data['profile_id'])
            obj, flag = AddressBookItem.objects.get_or_create(user = request.user, profile = profile_obj)
            return Response({'message': "Profile added to address book"}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({'error': 'Error adding address book item'}, status=status.HTTP_400_BAD_REQUEST)
        

class OrgansationView(APIView):

    def post(self, request):
        user_obj = User.objects.get(id = request.user.id)
        # members = json.loads(request.data["members"])
        organisation_serializer_obj = OrganisationSerializer(data = request.data)

        if organisation_serializer_obj.is_valid():
            organisation_obj = organisation_serializer_obj.save()
            group_obj = Group.objects.create(parent = None, name = organisation_obj.name, organisation = organisation_obj)
            group_obj.participants.add(request.user)
            group_obj.save()
            user_obj.organisation = organisation_obj
            user_obj.save()
            location_obj = Location.objects.create(name = "Global", organisation = organisation_obj)

            return Response({"organisation": organisation_serializer_obj.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(organisation_serializer_obj.errors, status=status.HTTP_400_BAD_REQUEST)

class GetTokenByPhoneOTP(APIView):

    permission_classes = [AllowAny, ]

    def post(self, request):
        try:
            phone_number = PhoneNumber.from_string(request.data['phone_number'])
            user = User.objects.get(phone_number = phone_number)
            phone_obj = PhoneVerification.objects.get(user = user, verified  = False)
            if phone_obj.otp == int(request.data['otp']) and (((datetime.datetime.utcnow().replace(tzinfo=utc) -  phone_obj.verification_time).total_seconds()/60) < 30) :
                phone_obj.verified = True
                user.phone_verified = True
                phone_obj.otp = None
                phone_obj.save()
                user.save()
                # login(request, user)
                auth_data = get_tokens_for_user(user)
                auth_data["is_staff"] = user.is_staff
                organisation_serializer_obj = OrganisationSerializer(user.organisation)
                auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                        "email": user.email,
                                        "phone_number": str(user.phone_number),
                                        "first_name": user.first_name,
                                        "last_name": user.last_name,
                                        "id": user.id
                                        }
                return Response({'data': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
            else:
                return Response({'data': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({'error': 'Invalid Number or OTP'}, status=status.HTTP_400_BAD_REQUEST)

class CheckOtp(APIView):

    permission_classes = [AllowAny, ]

    def post(self, request):
        try:
            email = request.data.get('email')
            phone_number = request.data.get('phone_number')
            otp = request.data.get('otp')
            verification_type = request.data.get('type')
            if (verification_type == 'email'):
                user = User.objects.get(email = email)
                phone_ver_obj = ResetPasswordVerification.objects.get(user = user, updated  = False)
                if phone_ver_obj.otp == otp:
                    return Response({'data': 'Correct OTP'}, status=status.HTTP_200_OK)
                else:
                    print("ab1")
                    return Response({'error': 'Invalid Number or OTP'}, status=status.HTTP_400_BAD_REQUEST)
            elif (verification_type == 'phone'):
                user = User.objects.get(phone_number = phone_number)
                phone_ver_obj = PhoneVerification.objects.get(user = user, verified  = False)
                if phone_ver_obj == otp:
                    return Response({'data': 'Correct OTP'}, status=status.HTTP_200_OK)
                else:
                    print("ab2")
                    return Response({'error': 'Invalid Number or OTP'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print("ab3")
                return Response({'error': 'Invalid Number or OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("ab4", e)
            return Response({'error': 'Invalid Number or OTP'}, status=status.HTTP_400_BAD_REQUEST)

class CreateMembersView(APIView):

    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user_obj = User.objects.get(id = request.user.id)
        members = request.data["members"]

        not_added_list = []
        for user_obj_dict in members:
            input_string = "sagg sagag(bcb3c47e-c74e-4779-a24f-bc529f7b69c0)"
            uuid_pattern = re.compile(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})')
            print(user_obj_dict)
            match = uuid_pattern.search(user_obj_dict["Branch"])

            if match:
                extracted_uuid = match.group(1)
                branch_obj = Branch.objects.filter(id = extracted_uuid).first()
                if not branch_obj:
                    not_added_list.append({
                    "email": user_obj_dict["Email"],
                    "error": "Invalid Branch"
                    })
                    continue
            else:
                not_added_list.append({
                    "email": user_obj_dict["Email"],
                    "error": "Invalid Branch"
                })
                continue
            already_present =User.objects.filter(email = user_obj_dict["Email"]).first()
            already_temp = TempUser.objects.filter(email = user_obj_dict["Email"]).first()
            reference_date = datetime.datetime(1900, 1, 1)
            target_date = reference_date + datetime.timedelta(days=user_obj_dict['Date Of Birth'])
            print(user_obj_dict)
            if not already_present and not already_temp:
                
                new_user_obj = TempUser.objects.create(first_name = user_obj_dict["First Name"],
                                                   last_name = user_obj_dict["Last Name"],
                                                   email = user_obj_dict["Email"],
                                                   organisation = request.user.organisation,
                                                   date_of_birth = target_date,
                                                   phone_number = user_obj_dict["Phone"],
                                                   onboarding_complete = False
                                                   )
                user_profile_obj = TempUserProfile.objects.create(user = new_user_obj)
                user_profile_obj.gender = user_obj_dict['Gender']
                user_profile_obj.education = user_obj_dict['Education']
                user_profile_obj.experience = user_obj_dict['Experience']
                user_profile_obj.branch = branch_obj
                user_profile_obj.save()
                # link_uuid = uuid.uuid4()
                onboard_obj = OnboardingLink.objects.create(user = new_user_obj, android_deeplink_code = generate_random_string(10), link_to_email = user_obj_dict["Email"])
                email_data = {
                    "receiver_name": user_obj_dict["First Name"],
                    "link": f"https://antro.page.link/?link=http://dev.antrocorp.com/?secret={onboard_obj.android_deeplink_code}&apn=com.antro"
                }
                TempUserStatus.objects.create(first_name = user_obj_dict["First Name"],
                                                   last_name = user_obj_dict["Last Name"],
                                                   email = user_obj_dict["Email"],
                                                   organisation = request.user.organisation,
                                                   date_of_birth = target_date,
                                                   phone_number = user_obj_dict["Phone"],
                                                   upload_status = 'pending'
                                                   )
                send_notification([user_obj_dict["Email"]], "new_onboard", email_data)

            else:
                not_added_list.append({
                    "email": user_obj_dict["Email"],
                    "error": "User already present"
                })
                TempUserStatus.objects.create(first_name = user_obj_dict["First Name"],
                                                   last_name = user_obj_dict["Last Name"],
                                                   email = user_obj_dict["Email"],
                                                   organisation = request.user.organisation,
                                                   phone_number = user_obj_dict["Phone"],
                                                   date_of_birth = target_date,
                                                   upload_status = 'failed',
                                                   failed_reason = "User already present"
                                                   )
            organisation_obj = request.user.organisation
            # organisation_obj.initial_members_added = True
            organisation_obj.save()

        return Response({"status": "Members added",
                             "members_not_added": not_added_list}, status=status.HTTP_201_CREATED)
    
class DLinkSecretDetails(APIView):

    permission_classes = [AllowAny, ]

    def get(self, request, secret):
        try:
            onboard_obj = OnboardingLink.objects.get(android_deeplink_code = secret)
            temp_user_obj = onboard_obj.user
            temp_user_obj.otp = random.randint(1000, 9999)
            temp_user_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
            temp_user_obj.merged = False
            temp_user_obj.save()
            if (temp_user_obj.phone_number):
                send_verification_otp(temp_user_obj.phone_number, temp_user_obj.otp)
            if (temp_user_obj.email):
                send_email_account_merge_otp(temp_user_obj.email, temp_user_obj.otp)
            data = {
                "email": onboard_obj.user.email,
                "first_name": onboard_obj.user.first_name,
                "last_name": onboard_obj.user.last_name,
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"error": "Invalid Code"}, status=status.HTTP_404_NOT_FOUND)



class CreateMembersHistoryView(APIView):

    permission_classes = [IsAuthenticated, ]

    def get(self, request): 
        # grouped_data = TempUserStatus.objects.filter(organisation = request.user.organisation).annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id'))
        # print(grouped_data[0])
        queryset = TempUserStatus.objects.filter(organisation_id=request.user.organisation)

        grouped_data = queryset.annotate(date=TruncDate('created_at')).values('date').annotate(objects=F('id'))

        result_data = {item['date'].strftime('%Y/%m/%d'): [] for item in grouped_data}

        serializer = TempUserStatusSerializer(queryset, many=True)

        for item in serializer.data:
            date_str = item['created_at'].strftime('%Y/%m/%d')
            result_data[date_str].append(item)
        # serializer = TempUserStatusSerializer(grouped_data, many=True)

        return Response(result_data)

class DocumentUpload(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract data from the request
        category_id = request.data.get('category_id')
        file = request.data.get('file')

        # Validate category_id and get the category
        try:
            category = DocumentCategory.objects.get(pk=category_id)
        except DocumentCategory.DoesNotExist:
            return Response({"error": "Category does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Create a new document
        user = request.user
        document = Document(category=category, user=user, file=file)

        # Save the document
        document.save()

        # Serialize the document
        serializer = DocumentSerializer(document)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class AddUserProfilePicture(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Check if the user is authenticated

        # Extract data from the request
        file = request.data.get('file')

        # Validate category_id and get the category
        try:
            user_obj = User.objects.get(id = request.user.id)
            user_profile_obj = UserProfile.objects.get(user = user_obj)
            user_profile_obj.image = file
            user_profile_obj.save()
        except DocumentCategory.DoesNotExist:
            return Response({"error": "Image not saved"}, status=status.HTTP_404_NOT_FOUND)
        serailizer_data = UserProfileSerializer(user_profile_obj)
        return Response(serailizer_data.data, status=status.HTTP_201_CREATED)

class DocumentDelete(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, document_id, format=None):
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response({"error": "Document does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the owner of the document
        if document.user != request.user:
            return Response({"error": "You are not the owner of this document"}, status=status.HTTP_403_FORBIDDEN)

        document.active = False
        document.save()
        return Response({"message": "Document deleted successfully"}, status=status.HTTP_200_OK)
    
class DocumentCategoryView(APIView):
    
    def get(self, request):
        data = DocumentCategory.objects.all()
        serializer_obj = DocumentCategorySerializer(data, many = True)
        return Response({'data': serializer_obj.data}, status=status.HTTP_200_OK)
    

class DocumentList(generics.ListAPIView):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        user = self.request.user
        return Document.objects.filter(user=user, active = True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Create a dictionary to group documents by category name
        categorized_documents = {}
        for doc in serializer.data:
            category_name = doc['category_name']
            if category_name not in categorized_documents:
                categorized_documents[category_name] = []
            categorized_documents[category_name].append(doc)
        
        return Response(categorized_documents, status=status.HTTP_200_OK)
    

class DeactivateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Set is_active to False for the user
        request.user.active = False
        request.user.save()
        user = request.user

        # Log out the user by blacklisting all existing tokens
       
        # outstanding_tokens = OutstandingToken.objects.filter(
        #     user=user)
        # for token in outstanding_tokens:
        #     print(token.__dict__)
        #     token.blacklisted = True
        #     token.save()

        # Update related tables where the user is used as a foreign key
        # For example, if UserProfile has a foreign key to User:
        UserProfile.objects.filter(user=request.user).update(active=False)

        # You can add more related models and update them similarly

        return Response({"message": "User deactivated and logged out from all devices."}, status=status.HTTP_200_OK)
    

class GetUserBySecret(APIView):

    permission_classes = [AllowAny]

    def get(self, request, secret, format=None):
        try:
            # Retrieve the OnboardingLink object with the provided secret
            onboarding_link = OnboardingLink.objects.get(secret=secret)

            # Retrieve the associated user
            user = User.objects.filter(email = onboarding_link.link_to_email).first()
            if user:
                # You can serialize the user data here if needed
                user_data = {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "organisation": user.organisation.name if user.organisation else None,
                }

                return Response(user_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User not found",
                                 "email": onboarding_link.link_to_email}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Onboarding link not found"}, status=status.HTTP_404_NOT_FOUND)
        
    
class AddUserBySecret(APIView):

    permission_classes = [AllowAny]

    def post(self, request, format=None):
        try:
            merge_type = request.data.get('type') # new or existing 
            secret = request.data.get('secret')
            # Retrieve the OnboardingLink object with the provided secret
            if (merge_type == 'new'):
                password = request.data.get('password')
                onboarding_link = OnboardingLink.objects.get(secret=secret)
                cor_user_obj = User.objects.get(id = onboarding_link.user.id)
                cor_user_obj.onboarding_complete = True
                cor_user_obj.set_password(password)
                cor_user_obj.save()

                onboarding_link = OnboardingLink.objects.get(secret=secret)

                # Retrieve the associated user
            elif (merge_type == 'old'):

                password = request.data.get('password')
                onboarding_link = OnboardingLink.objects.get(secret=secret)

        except Exception as e:
            return Response({"error": "Onboarding link not found"}, status=status.HTTP_404_NOT_FOUND)
        

class SearchUsers(APIView):

    permission_classes = [AllowAny]

    def get(self, request, keyword):
        queryset = User.objects.filter(
            Q(first_name__icontains=keyword) |
            Q(last_name__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(phone_number__icontains=str(keyword))
        )
        profile_queryset = Profile.objects.filter(
            Q(first_name__icontains=keyword) |
            Q(last_name__icontains=keyword) |
            Q(email__icontains=keyword) |
            Q(phone_number__icontains=str(keyword))
        )
        extracted_users = [obj.user for obj in profile_queryset]
        merged_users = set(queryset) | set(extracted_users)

        # Convert the set back to a list if needed
        merged_users_list = list(merged_users)
        serializer_obj = HiddenUserSerializer(merged_users_list, many = True)
        return Response({'data': serializer_obj.data}, status=status.HTTP_200_OK)

class MergeAccount(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user_id = request.data.get('user_id') # new or existing 
            # Retrieve the OnboardingLink object with the provided secret
            old_user = User.objects.filter(user_id = user_id).first()
            if (old_user):
                request_obj, flag = AccountMergeRequest.objects.get_or_create(user = request.user, from_account = old_user)
                request_obj.otp = random.randint(1000, 9999)
                request_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
                request_obj.merged = False
                request_obj.save()
                if (old_user.phone_number):
                    send_verification_otp(old_user.phone_number, request_obj.otp)
                if (old_user.email):
                    send_email_account_merge_otp(old_user.email, request_obj.otp)
                return Response({'data': "OTP sent"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid account"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": "Invalid account"}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request):
        try:
            user_id = request.data.get('user_id') # new or existing 
            # Retrieve the OnboardingLink object with the provided secret
            otp = request.data.get('otp') 
            old_user = User.objects.filter(user_id = user_id).first()
            if (old_user):
                request_obj = AccountMergeRequest.objects.get(user = request.user, from_account = old_user, merged = False)
                if request_obj.otp == otp and (((datetime.datetime.utcnow().replace(tzinfo=utc) -  request_obj.verification_time).total_seconds()/60) < 30):
                    request_obj.merged = True
                    request_obj.save()
                # return Response({'data': 'Account verified'}, status=status.HTTP_200_OK)


                request_obj.otp = random.randint(1000, 9999)
                request_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
                request_obj.merged = False
                request_obj.save()
                old_profiles = Profile.objects.filter(user = old_user)
                for profile in old_profiles:
                    profile.user = request_obj.user
                    profile.save()
                old_user.active = False
                old_user.save()
                return Response({'data': "Account merged"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid account"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response({"error": "Invalid account"}, status=status.HTTP_404_NOT_FOUND)
        

class ProfileCommentListCreateView(generics.ListCreateAPIView):
    queryset = ProfileComment.objects.all()
    serializer_class = ProfileCommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProfileCommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProfileComment.objects.all()
    serializer_class = ProfileCommentSerializer
    permission_classes = [IsAuthenticated]


class ProfileLikeCreateView(generics.CreateAPIView):
    queryset = ProfileLike.objects.all()
    serializer_class = ProfileLikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        profile = serializer.validated_data['profile']

        # Check if the user has already liked the profile
        if ProfileLike.objects.filter(user=user, profile=profile).exists():
            raise serializers.ValidationError("You have already liked this profile.")

        # Save the like if the user has not already liked the profile
        serializer.save(user=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProfileLikeDestroyView(generics.DestroyAPIView):
    queryset = ProfileLike.objects.all()
    serializer_class = ProfileLikeSerializer
    permission_classes = [IsAuthenticated]

import io
import os
import tempfile
import time
import boto3
from django.core.files.storage import FileSystemStorage

class SmartFindUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        video_file = request.data.get('video_file')
        authentication_entity_id = request.data.get('authentication_entity_id')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        date_of_birth = request.data.get('date_of_birth')
        

        # try:
        print("token:", authentication_entity_id)
        authentication_entity_obj = AuthenticationEntity.objects.filter(id = authentication_entity_id).first()
        
        if not authentication_entity_obj:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        authentication_entity_obj.first_name = first_name
        authentication_entity_obj.last_name = last_name
        authentication_entity_obj.date_of_birth = date_of_birth
        authentication_entity_obj.save()
        if not video_file:
            return Response({'error': 'Missing video file'}, status=status.HTTP_400_BAD_REQUEST)
        # Create a unique filename for the video
        filename = f'uploaded_video_{int(time.time())}.mp4'  # Adjust extension as needed
        local_storage = FileSystemStorage(location=os.path.join(settings.BASE_DIR,'staticfiles'))  # Adjust path as needed

        # Save the video to S3
        with local_storage.open(filename, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        # abc = test.delay(name="aname")
        # print(abc)
        perform_user_detection.delay(filename, authentication_entity_id, first_name, last_name, date_of_birth)

        return Response({"Status": "success", "message": "Request submitted"}, status=status.HTTP_201_CREATED)
        # except Exception as e:
        #     print(e)
        #     return Response({'error': 'Error creating authentication entity'}, status=status.HTTP_400_BAD_REQUEST)
    

class CreateAuthenticationEntity(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        try:

            gestures = ["fist", "open_hand", "thumbs_up", "thumbs_down"]
            gesture_obj = HandGesture.objects.filter(name = random.choice(gestures)).first()
            gesture_obj = HandGesture.objects.filter(name = 'fist').first()
            # authentication_entity_obj = AuthenticationEntity.objects.create(otp = 4321, gesture = gesture_obj.name)

            authentication_entity_obj = AuthenticationEntity.objects.create(otp = random.randint(1000, 9999), gesture = gesture_obj.name)
            data = {
                "id": authentication_entity_obj.id,
                "gesture": authentication_entity_obj.gesture,
                "gesture_url": gesture_obj.url,
                "otp": authentication_entity_obj.otp
            }
            return Response({"Status": "Created", "data": data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': 'Error creating authentication entity'}, status=status.HTTP_400_BAD_REQUEST)



class CheckAuthenticationEntity(APIView):
    """
    API view to check the authentication entity
    """
    permission_classes = [AllowAny]

    def get(self, request, authentication_entity_id):
        """
        Get method to check the authentication entity
        Args:
            request: request object
            authentication_entity_id: id of the authentication entity
        Returns:
            Response with the status and data
        """
        try:
            authentication_entity_obj = AuthenticationEntity.objects.get(id=authentication_entity_id)
            # Check if the authentication entity status is 1 and created within the last 24 hours
            # twenty_four_hours_ago = timezone.now() - datetime.timedelta(hours=24)
            print(authentication_entity_obj.status == "1", ((timezone.now() - authentication_entity_obj.created_at).total_seconds()))
            if authentication_entity_obj.status == "1" and ((timezone.now() - authentication_entity_obj.created_at).total_seconds() <= 86400) and authentication_entity_obj.user:
                data = {
                    "id": authentication_entity_obj.id,
                    "status": authentication_entity_obj.get_status_display(),
                    "auth_data": get_tokens_for_user(authentication_entity_obj.user)
                }
            else:
                data = {
                    "id": authentication_entity_obj.id,
                    "status": authentication_entity_obj.get_status_display()
                }
            
            # Return the response with the status and data
            return Response({"Status": "success", "data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            # Return error response if there's an exception
            print(e)
            return Response({'error': 'Error validating authentication entity'}, status=status.HTTP_400_BAD_REQUEST)
        
class DataExistCheck(APIView):
    """
    API view to check the existence of data based on type
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get method to handle data existence check
        :param request: request object
        :return: response indicating the availability of data
        """
        try:
            data = {
                "type": request.GET.get('type'),
                "value": request.GET.get('value')
            }
            print(data)
            if data["type"] == "user_id":
                data_exists = User.objects.filter(user_id=data["value"]).exists()
            elif data["type"] == "email":
                data_exists = User.objects.filter(email=data["value"]).exists()
            elif data["type"] == "phone":
                data_exists = User.objects.filter(phone_number=data["value"]).exists()
            else:
                return Response({"data_available": True}, status=status.HTTP_200_OK)
            return Response({"data_available": not data_exists}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Getting data available: ", str(e))
            return Response({'error': 'Error validating'}, status=status.HTTP_400_BAD_REQUEST)
        
class CreateUserFromAuthEntity(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        phone_number = request.data.get('phone_number')
        email = request.data.get('email')
        user_id = request.data.get('user_id')
        authentication_entity_id = request.data.get('authentication_entity_id')
        authentication_entity_obj = AuthenticationEntity.objects.get(id=authentication_entity_id)
        user = None
        if authentication_entity_obj.user:
            existing_user = authentication_entity_obj.user
            if User.objects.filter(Q(email=email) | Q(phone_number=phone_number) | Q(user_id=user_id)).exclude(id=existing_user.id).exists():
                return Response({"message": "Email, phone number, or user_id already exists in another user"}, status=status.HTTP_400_BAD_REQUEST)

            # Update existing user's email, phone number, or user_id if not already set
            if email:
                existing_user.email = email
            if phone_number:
                existing_user.phone_number = phone_number
            if user_id:
                existing_user.user_id = user_id
            existing_user.save()
            user = existing_user
            print("here1 ", authentication_entity_obj.user)
        else:
            if user_id:
                user_id_exists = User.objects.filter(user_id=user_id).exists()
                if user_id_exists:
                    return Response({"message": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    authentication_entity_obj.user_id_string = user_id
            if email:
                email_exists = User.objects.filter(email=email).exists()
                if email_exists:
                    return Response({"message": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    authentication_entity_obj.email = email
            if phone_number:
                phone_exists = User.objects.filter(phone_number=phone_number).exists()
                if phone_exists:
                    return Response({"message": "Phone number already exists"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    authentication_entity_obj.phone_number = phone_number
            authentication_entity_obj.save()
            user = User.objects.create(user_id=user_id, email=email, phone_number=phone_number, first_name = authentication_entity_obj.first_name, last_name = authentication_entity_obj.last_name, date_of_birth = authentication_entity_obj.date_of_birth)
            user.first_name = authentication_entity_obj.first_name
            user.last_name = authentication_entity_obj.last_name
            user.date_of_birth = authentication_entity_obj.date_of_birth
            user.save()
            authentication_entity_obj.user = user
            authentication_entity_obj.save()
            AuthenticationEntity.objects.filter(user = user).exclude(id = authentication_entity_obj.id).delete()
            print("here2 ", authentication_entity_obj.user)
        # user_profile_obj = UserProfile.objects.get(user = user)
        serailizer_data = UserSerializer(user)
        return Response({"message": "User created", "data": serailizer_data.data}, status=status.HTTP_201_CREATED)
    

class SendEmailPhoneOtp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        verify_type = request.data.get('type')
        authentication_entity_id = request.data.get('authentication_entity_id')
        try:
            authentication_entity_obj = AuthenticationEntity.objects.get(id=authentication_entity_id)
            if (verify_type == "phone"):
                phone_verify_obj = PhoneVerification.objects.get(user = authentication_entity_obj.user)
                phone_verify_obj.otp = random.randint(1000, 9999)
                phone_verify_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
                phone_verify_obj.save()
                send_verification_otp(authentication_entity_obj.user.phone_number, phone_verify_obj.otp)
                return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)
            elif (verify_type == "email"):
                email_verify_obj = EmailVerification.objects.get(user = authentication_entity_obj.user)
                email_verify_obj.otp = random.randint(1000, 9999)
                email_verify_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
                email_verify_obj.save()
                send_email_verification_otp(authentication_entity_obj.user.email, email_verify_obj.otp)
                return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Sending OTP: ", str(e))
            return Response({"message": "Error sending OTP"}, status=status.HTTP_400_BAD_REQUEST)