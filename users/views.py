from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import  Response
from rest_framework.views import APIView
from .utils import get_tokens_for_user
from django.db.models import Q
from rest_framework_simplejwt.tokens import OutstandingToken
from users.models import User, PhoneVerification, UserProfile, RequestData, AddressBookItem,\
Document, DocumentCategory, OnboardingLink, EmailVerification, ResetPasswordVerification, TempUser , TempUserProfile
from .serializers import RegistrationSerializer, PasswordChangeSerializer, UserSerializer, UserProfileSerializer, \
AddressBookItemSerializer, OrganisationSerializer, DocumentSerializer, DocumentCategorySerializer, detect_email_or_phone, HiddenUserSerializer
from .utils import send_verification_otp, send_reset_password_otp, send_email_verification_otp
from django.shortcuts import get_object_or_404
from django.utils.timezone import utc
import json
import random
import datetime
import uuid
from profiles.models import Profile
from organisation.models import Group, Branch, Location
from push_notifications.models import WebPushDevice
import re
from users.utils import send_notification, generate_random_string
from phonenumber_field.phonenumber import PhoneNumber


class RegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user_obj = serializer.save()
            input_type = detect_email_or_phone(request.data.get('email'))
            if input_type == 'email':
                user_profile_obj = UserProfile.objects.get(user = user_obj)
                user_profile_obj.designation = request.data.get('designation')
                user_profile_obj.save()
                profile_obj = Profile.objects.get(user = user_obj)
                profile_obj.first_name = user_obj.first_name
                profile_obj.last_name = user_obj.last_name
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




      
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        
       
        input_type = detect_email_or_phone(request.data.get('email'))
        if input_type == 'email':
            if 'email' not in request.data or 'password' not in request.data:
                return Response({'data': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
            email = request.data.get('email')
            password = request.data.get('password')
            user_obj = User.objects.filter(email = request.data.get('email'), email_verified = True).first()
            if not user_obj:
                 return Response({'data': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            user = authenticate(request, username=user_obj.user_id, password='password')
            if user is not None:
                if not user.active:
                    return Response({'data': 'Invalid Credentialfs' + str(user.active)}, status=status.HTTP_401_UNAUTHORIZED)
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
        elif input_type == 'phone':
            user_obj = User.objects.filter(phone_number = request.data.get('email'), phone_verified = True).first()
            if not user_obj:
                user_obj = User.objects.filter(phone_number = request.data.get('email')).first()
                if not user_obj:
                    user_obj = User(phone_number=request.data.get('email')
                            )
                    user_obj.set_password(generate_random_string())
                    user_obj.save()
            phone_verification_obj, flag = PhoneVerification.objects.get_or_create(user = user_obj)
            phone_verification_obj.otp = random.randint(100000, 999999)
            phone_verification_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
            phone_verification_obj.verified = False
            phone_verification_obj.save()
            send_verification_otp(user_obj.phone_number, phone_verification_obj.otp)
            return Response({'data': 'OTP Sent'}, status=status.HTTP_200_OK)
        else:
            return Response({'data': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            # user = authenticate(request, email=email, password=password)
        
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

    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get('otp')
        verification_type = request.data.get('type')
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        try:
            user = User.objects.get(email = email)
            if (verification_type == "phone"):

                phone_obj = PhoneVerification.objects.get(user = user)
                if phone_obj.otp == otp and (((datetime.datetime.utcnow().replace(tzinfo=utc) -  phone_obj.verification_time).total_seconds()/60) < 30) :
                    phone_obj.verified = True
                    phone_obj.save()
                    user.phone_verified = True
                    user.save()
                    return Response({'data': 'Account verified'}, status=status.HTTP_200_OK)
                else:
                    return Response({'data': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            elif (verification_type == "email"):
                email_obj = EmailVerification.objects.get(user = user, verified = False)
                if email_obj.verification_time > datetime.datetime.utcnow().replace(tzinfo=utc) and email_obj.otp == int(otp):
                    email_obj.verified = True
                    email_obj.otp = None
                    email_obj.save()
                    user.email_verified = True
                    user.save()
                    return Response({'data': 'Email verified'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Invalid or expired otp'}, status=status.HTTP_400_BAD_REQUEST)
            elif (verification_type == "reset_password"):
                reset_password_obj = ResetPasswordVerification.objects.get(user = user)
                if reset_password_obj.verification_time > datetime.datetime.utcnow().replace(tzinfo=utc) and reset_password_obj.otp == int(otp):
                    reset_password_obj.updated = True
                    reset_password_obj.otp = None
                    reset_password_obj.save()
                    user.set_password(new_password)
                    user.save()

                    return Response({'data': 'Password resetted'}, status=status.HTTP_200_OK)
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
        otp = request.data.get('otp')
        verification_type = request.data.get('type')
        email = request.data.get('email')

        try:
            user = User.objects.get(email = email)
            if (verification_type == "email_verification"):

                email_obj = EmailVerification.objects.get(user = user)
                email_obj.otp = random.randint(100000, 999999)
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
            reset_obj.otp = random.randint(100000, 999999)
            reset_obj.verification_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
            send_reset_password_otp(user_obj.email, reset_obj.otp)
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

class GetTokenByPhoneOTP(APIView):

    permission_classes = [AllowAny, ]

    def post(self, request):
        try:
            phone_number = PhoneNumber.from_string(request.data['phone_number'])
            user = User.objects.get(phone_number = phone_number)
            print(user, "KAKAKJSJf")
            phone_obj = PhoneVerification.objects.get(user = user, verified  = False)
            if phone_obj.otp == int(request.data['otp']) and (((datetime.datetime.utcnow().replace(tzinfo=utc) -  phone_obj.verification_time).total_seconds()/60) < 30) :
                phone_obj.verified = True
                user.phone_verified = True
                phone_obj.save()
                user.save()
                # login(request, user)
                auth_data = get_tokens_for_user(user)
                auth_data["is_staff"] = user.is_staff
                organisation_serializer_obj = OrganisationSerializer(user.organisation)
                auth_data['user_data'] = {"organisation": organisation_serializer_obj.data,
                                        "email": user.email,
                                        "phone": str(user.phone_number),
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


class CreateMembersView(APIView):

    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user_obj = User.objects.get(id = request.user.id)
        members = json.loads(request.data["members"])

        not_added_list = []
        for user_obj_dict in members:
            input_string = "sagg sagag(bcb3c47e-c74e-4779-a24f-bc529f7b69c0)"
            uuid_pattern = re.compile(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})')
            match = uuid_pattern.search(user_obj_dict["Branch"])

            if match:
                extracted_uuid = match.group(1)
                branchObj = Branch.objects.filter(id = extracted_uuid).first()
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
                reference_date = datetime.datetime(1900, 1, 1)
                target_date = reference_date + datetime.timedelta(days=user_obj_dict['Date Of Birth'])
                pass
                new_user_obj = TempUser.objects.create(first_name = user_obj_dict["First Name"],
                                                   last_name = user_obj_dict["Last Name"],
                                                   email = user_obj_dict["Email"],
                                                   organisation = request.user.organisation,
                                                   date_of_birth = target_date,
                                                   onboarding_complete = False
                                                   )
                user_profile_obj = TempUserProfile.objects.create(user = new_user_obj)
                user_profile_obj.phone = user_obj_dict['Phone']
                user_profile_obj.gender = user_obj_dict['Gender']
                user_profile_obj.Education = user_obj_dict['Education']
                user_profile_obj.Experience = user_obj_dict['Experience']
                user_profile_obj.branch = branchObj
                user_profile_obj.save()
                link_uuid = uuid.uuid4()
                onboard_obj = OnboardingLink.objects.create(user = new_user_obj, secret = link_uuid, link_to_email = user_obj_dict["Email"])
                email_data = {
                    "receiver_name": user_obj_dict["First Name"],
                    "link": f"http://localhost:8000/new_onboard_link/{onboard_obj.secret}/"
                }
                send_notification([user_obj_dict["Email"]], "new_onboard", email_data)

            else:
                not_added_list.append({
                    "email": user_obj_dict["Email"],
                    "error": "User already present"
                })
            organisation_obj = request.user.organisation
            # organisation_obj.initial_members_added = True
            organisation_obj.save()

        return Response({"status": "Members added",
                             "members_not_added": not_added_list}, status=status.HTTP_201_CREATED)
    


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
            Q(email__icontains=keyword)
        )
        serializer_obj = HiddenUserSerializer(queryset, many = True)
        return Response({'data': serializer_obj.data}, status=status.HTTP_200_OK)