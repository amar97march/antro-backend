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

