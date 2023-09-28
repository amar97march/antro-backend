from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import  Response
from rest_framework.views import APIView
from .utils import get_tokens_for_user
from users.models import User, PhoneVerification, UserProfile, RequestData, AddressBookItem
from .serializers import RegistrationSerializer, PasswordChangeSerializer, UserSerializer, UserProfileSerializer, \
AddressBookItemSerializer, OrganisationSerializer
from .utils import send_verification_otp
from django.shortcuts import get_object_or_404
from django.utils.timezone import utc
import json
import datetime
from profiles.models import Profile
from organisation.models import Group, Branch, Location
from rest_framework.permissions import IsAuthenticated, AllowAny
from push_notifications.models import WebPushDevice
import re


class RegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserData(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            user_obj = User.objects.get(id = request.user.id)
            organisation_serializer_obj = OrganisationSerializer(user_obj.organisation)
            data = {
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




      
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'data': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        email = request.data.get('email')
        print("Data: ", request.data.get('email'))
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            auth_data = get_tokens_for_user(request.user)
            phone_obj = PhoneVerification.objects.get(user = user)
            print(auth_data, user, phone_obj.verified)
            auth_data["verified"] = phone_obj.verified
            auth_data["is_staff"] = user.is_staff
            organisation_serializer_obj = OrganisationSerializer(user.organisation)
            auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                      "email": email,
                                      "first_name": user.first_name,
                                      "last_name": user.last_name
                                      }
        #     WebPushDevice.objects.create(
        #         registration_id=user.id,
        #         p256dh=request.GET.get('p256dh'),
        #         auth=request.GET.get('auth'),
        #         browser=request.GET.get('browser'),
        #         user=request.user,
        # )
            return Response({'data': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
        return Response({'data': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class SendOTP(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user:
            return Response({'data': 'Invalid account missing'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = request.user
        country_code = request.data.get('country_code')
        phone = request.data.get('phone')
        otp = send_verification_otp(f'+{country_code}{phone}')
        if otp:

            phone_obj = PhoneVerification.objects.get(user = user)
            phone_obj.otp = otp
            phone_obj.verification_time = datetime.datetime.now()
            phone_obj.save()
            return Response({'data': 'Otp send successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'data': 'OTP not send. Please try after sometime'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        otp = request.data.get('otp')
        user = request.user
        phone_obj = PhoneVerification.objects.get(user = user)
        if phone_obj.otp == otp and (((datetime.datetime.utcnow().replace(tzinfo=utc) -  phone_obj.verification_time).total_seconds()/60) < 30) :
            phone_obj.verified = True
            phone_obj.save()
            return Response({'data': 'Account verified'}, status=status.HTTP_200_OK)
        else:
            return Response({'data': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


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
            print()
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


class CreateMembersView(APIView):

    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user_obj = User.objects.get(id = request.user.id)
        members = json.loads(request.data["members"])
        print("ABABA ", len(members))

        not_added_list = []
        for user_obj_dict in members:
            input_string = "sagg sagag(bcb3c47e-c74e-4779-a24f-bc529f7b69c0)"
            uuid_pattern = re.compile(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})')
            match = uuid_pattern.search(user_obj_dict["Branch"])

            if match:
                extracted_uuid = match.group(1)
                print(extracted_uuid)
                branchObj = Branch.objects.filter(id = extracted_uuid).first()
                print(branchObj)
                if not branchObj:
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
            
            if not already_present:
                print(user_obj_dict['Date Of Birth'])
                reference_date = datetime.datetime(1900, 1, 1)
                target_date = reference_date + datetime.timedelta(days=user_obj_dict['Date Of Birth'])
                pass
                new_user_obj = User.objects.create(first_name = user_obj_dict["First Name"],
                                                   last_name = user_obj_dict["Last Name"],
                                                   email = user_obj_dict["Email"],
                                                   password = "klfashglakfihifiaeknf",
                                                   organisation = request.user.organisation,
                                                   date_of_birth = target_date
                                                   )
                user_profile_obj = UserProfile.objects.get(user = new_user_obj)
                user_profile_obj.phone = user_obj_dict['Phone']
                user_profile_obj.gender = user_obj_dict['Gender']
                user_profile_obj.Education = user_obj_dict['Education']
                user_profile_obj.Experience = user_obj_dict['Experience']
                user_profile_obj.branch = branchObj
                user_profile_obj.save()

            else:
                not_added_list.append({
                    "email": user_obj_dict["Email"],
                    "error": "User already present"
                })
            organisation_obj = request.user.organisation
            organisation_obj.initial_members_added = True
            organisation_obj.save()

        return Response({"status": "Members added",
                             "members_not_added": not_added_list}, status=status.HTTP_201_CREATED)