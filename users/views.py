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
AddressBookItemSerializer
from .utils import send_verification_otp
from django.shortcuts import get_object_or_404
from django.utils.timezone import utc
import datetime
from profiles.models import Profile
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.


class RegistrationView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
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