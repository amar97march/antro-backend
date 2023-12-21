from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import  Response
from rest_framework.views import APIView
from .serializers import ProfileSerializer
from django.utils.timezone import utc
import datetime
from .models import Keyword, Profile
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db.models.functions import Distance
import qrcode
from users.models import UserProfile
from users.serializers import UserProfileSerializer
from io import BytesIO
from django.core.files.base import ContentFile
import random

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            
            data = request.data
            data["user"] = request.user.id
            print('AWFAS')
            # print(data)
            keywords = []
            print('AWFAS')
            for item in data['keywords']:
                # print(item)
                keyword_obj, created = Keyword.objects.get_or_create(name = item)
                keywords.append(keyword_obj.id)
            # print(keywords)
            data['keywords'] = keywords
            longitude = data['location']['longitude']
            latitude = data['location']['latitude']
            print('AWFAS')
            location = fromstr(f'POINT({longitude} {latitude})', srid=4326)
            print("atqw")
            data['location'] = location
            print(data)


            feedback_serializer = ProfileSerializer(data=request.data)
            if not feedback_serializer.is_valid():
                return Response({
                    'message': feedback_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            feedback_serializer.save()
            return Response({
                'message': 'successfully added profile'
            })

        except Exception as e:
            print(e)
            return Response({
                'message': 'Error creating profile',
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
        
class SearchProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            queryset = Profile.objects.all().order_by('name')
            if request.data['location']:
                longitude = request.data['location']['longitude']
                latitude = request.data['location']['latitude']
                distance = request.data['location']['distance']

                user_location = fromstr(f'POINT({longitude} {latitude})', srid=4326)
                queryset = queryset.annotate(distance=Distance('location', user_location)).filter(distance__lte = distance)
                if 'profession' in request.data:
                    queryset = queryset.filter(profession__icontains = request.data['profession'])
            profile_serializer_obj = ProfileSerializer(queryset, many=True)
            return Response({
                'message': 'successfully retrieve profiles information',
                'data': profile_serializer_obj.data,
                'status_code': status.HTTP_200_OK
            })
        except Exception as e:
            print(e)
            return Response({
                'message': 'Error fetching profiles',
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

class MyProfilesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            queryset = Profile.objects.filter(user=request.user).order_by('first_name')
            profile_serializer_obj = ProfileSerializer(queryset, many=True)
            return Response({
                'message': 'successfully retrieve profiles information',
                'data': profile_serializer_obj.data,
                'status_code': status.HTTP_200_OK
            })
        except Exception as e:
            print(e)
            return Response({
                'message': 'Error fetching profiles',
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)



class ProfileData(APIView):

    def get(self, request, id):
        try:
            profile_obj = Profile.objects.get(antro_id=id)
            profile_serializer_obj = ProfileSerializer(profile_obj)
            return Response({
                'message': 'successfully retrieve profiles information',
                'data': profile_serializer_obj.data,
                'status_code': status.HTTP_200_OK
            })
        except Exception as e:
            print(e)
            return Response({
                'message': 'Error fetching profile',
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
        
class ProfileQR(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            profile_obj = Profile.objects.get(id=id)
            # profile_serializer_obj = ProfileSerializer(profile_obj)
            # return Response({
            #     'message': 'successfully retrieve profiles information',
            #     'data': profile_serializer_obj.data,
            #     'status_code': status.HTTP_200_OK
            # })
            # content = str(random.randint(1000, 9999))
            
            # Generate QR code
            text = profile_obj.antro_id
            # text = f"https://antro.page.link/?link=http://dev.antrocorp.com/?profile={profile_obj.antro_id}&apn=com.antro"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Save the image to a BytesIO buffer
            buffer = BytesIO()
            img.save(buffer, format="PNG")

            # Return the image in the API response
            response = HttpResponse(buffer.getvalue(), content_type='image/png')
            response['Content-Disposition'] = 'inline; filename="random_qrcode.png"'
            return response

        except Exception as e:
            print(e)
            return Response({
                'message': 'Error fetching profile',
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
        

class SetActiveProfile(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        profile_id = self.kwargs.get('profile_id')

        try:
            # Get the profile for the provided profile_id and the logged-in user
            profile_to_activate = Profile.objects.get(id=profile_id, user=user)

            # Set active_profile to True for the selected profile
            profile_to_activate.active_profile = True
            profile_to_activate.save()

            # Set active_profile to False for all other profiles of the user
            Profile.objects.exclude(id=profile_to_activate.id).filter(user=user).update(active_profile=False)

            # Serialize the updated profile
            serialized_profile = ProfileSerializer(profile_to_activate)

            return Response(serialized_profile.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found for the current user.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SaveProfile(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)
        profile_id = request.data.get('profile_id')

        try:
            profile_to_add = Profile.objects.get(id=profile_id)
            user_profile.profiles.add(profile_to_add)
            serialized_user_profile = UserProfileSerializer(user_profile)
            return Response(serialized_user_profile.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UnsaveProfile(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)
        profile_id = request.data.get('profile_id')

        try:
            profile_to_remove = Profile.objects.get(id=profile_id)
            user_profile.profiles.remove(profile_to_remove)
            serialized_user_profile = UserProfileSerializer(user_profile)
            return Response(serialized_user_profile.data, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSavedProfiles(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            user_profiles = user_profile.profiles.all()
            
            # Serialize the profiles
            serialized_profiles = ProfileSerializer(user_profiles, many=True)

            return Response({
                "user_profiles": serialized_profiles.data
            }, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)