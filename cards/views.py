from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import  Response
from rest_framework.views import APIView
from .serializers import CardSerializer
from django.utils.timezone import utc
import datetime
from .models import Keyword, Card
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db.models.functions import Distance

class CardView(APIView):
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


            feedback_serializer = CardSerializer(data=request.data)
            if not feedback_serializer.is_valid():
                return Response({
                    'message': feedback_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            feedback_serializer.save()
            return Response({
                'message': 'successfully added card'
            })

        except Exception as e:
            print(e)
            return Response({
                'message': 'Error creating card',
                'status_code': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
        
class SearchCardView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        queryset = Card.objects.all().order_by('name')
        if request.data['location']:
            longitude = request.data['location']['longitude']
            latitude = request.data['location']['latitude']
            distance = request.data['location']['distance']

            user_location = fromstr(f'POINT({longitude} {latitude})', srid=4326)
            queryset = queryset.annotate(distance=Distance('location', user_location)).filter(distance__lte = distance)
            if 'profession' in request.data:
                queryset = queryset.filter(profession__icontains = request.data['profession'])
        card_serializer_obj = CardSerializer(queryset, many=True)
        return Response({
            'message': 'successfully retrieve cards information',
            'data': card_serializer_obj.data,
            'status_code': status.HTTP_200_OK
        })

