from django.contrib.auth import get_user_model
from organisation.models import Group, Organisation, Location, Branch, BranchBroadcastHistory
from rest_framework.views import APIView
from chat.models import Chat, Contact
from chat.views import get_user_contact
from .serializers import GroupSerializer, LocationSerializer, BranchSerializer, BranchBroadcastHistorySerializer
from users.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
import openpyxl
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework.permissions import IsAuthenticated, AllowAny
from openpyxl.worksheet.datavalidation import DataValidation
from ..utils import broadcast_to_branches_by_list

User = get_user_model()


class BroadcastView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GroupSerializer(data = request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        organisation_id = request.query_params.get('organisation_id', None)
        parent_id = request.query_params.get('parent_id', None)

        group_list = Group.objects.filter(organisation = request.user.organisation, parent__id = parent_id)
        serializer_data = GroupSerializer(group_list, many=True)
        return Response({
            "status": 200,
            'message': 'Records found',
            'data': serializer_data.data
            })

    def get_queryset(self):
        queryset = Chat.objects.all()
        email = self.request.query_params.get('email', None)
        if email is not None:
            contact = get_user_contact(email)
            queryset = contact.chats.all()
        return queryset
    
class LocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LocationSerializer(data = request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        organisation_id = request.query_params.get('organisation_id', None)
        parent_id = request.query_params.get('parent_id', None)

        group_list = Location.objects.filter(organisation = request.user.organisation, parent__id = parent_id)
        serializer_data = LocationSerializer(group_list, many=True)
        return Response({
            "status": 200,
            'message': 'Records found',
            'data': serializer_data.data
            })
    
    def delete(self, request):
        try:
            location_obj = Location.objects.get(id = request.data.get("location_id", None), organisation = request.user.organisation)
            location_obj.delete()
            return Response({
                "status": 200,
                'message': 'Records deleted'
                })
        except Exception as e:
            return Response({'data': 'Record not found'}, status=status.HTTP_400_BAD_REQUEST)


class LocationBranchesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, id):

        location_obj = Location.objects.get(id = id)
        last_location_obj_lists = location_obj.get_level_5_objs()
        branches = Branch.objects.filter(location__in = last_location_obj_lists)
        branches_data = []
        for branch in branches:

            branches_data.append({
                "id": branch.id,
                "hierarchy": f"/{branch.location.parent.parent.parent.parent.parent.name}/{branch.location.parent.parent.parent.parent.name}/{branch.location.parent.parent.parent.name}/{branch.location.parent.parent.name}/{branch.location.parent.name}/{branch.location.name}/",
                "name": branch.branch_name
            })
        print("asgasg", branches)
        return Response({
            "status": 200,
            'message': 'Records found',
            'data': branches_data
            })


class SendBroadcast(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            message = request.data.get('message', [])
            branch_list = request.data.get('branch_list', [])
            print("ABABABABBABA", message, branch_list)
            location_obj = Location.objects.get(id = request.data.get('location_id', None))
            broadcast_to_branches_by_list(message, branch_list, request.user, location_obj)
            return Response({
                "status": 200,
                'message': 'Broadcast successfull'
                })
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class BranchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = BranchSerializer(data = request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        try:
            branch_obj = Branch.objects.get(id = request.data.get("branch_id", None), organisation = request.user.organisation)
            branch_obj.delete()
            return Response({
                "status": 200,
                'message': 'Records deleted'
                })

        
        except Exception as e:
            return Response({'data': 'Record not found'}, status=status.HTTP_400_BAD_REQUEST)



class ParticipantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        partipants_list = request.data.get('participants', [])
        group_id = request.data.get('group_id', None)

        partipants_obj_list = [User.objects.get(id=participant_id) for participant_id in partipants_list]
        print(partipants_obj_list)
        group_obj = Group.objects.get(id = group_id)
        group_obj.participants.add(*partipants_obj_list)
        group_obj.save()

        return Response({
            "status": 200,
            'message': 'Participants Added',
            })
        

class MyGroup(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        group_list = request.user.broadcast_groups.all()
        for grou in group_list:
            print(grou.participants)
        serializer_data = GroupSerializer(group_list, many=True)
        return Response({
            "status": 200,
            'message': 'Records found',
            'data': serializer_data.data
            })
    
class OrganisationMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            organistion_obj = Organisation.objects.get(id = request.user.organisation.id)

            users_list = User.objects.filter(organisation = organistion_obj)
            user_serializer_obj = UserSerializer(users_list, many=True)

            return Response({"members": user_serializer_obj.data})
        
        except Exception as e:
            print(e)
            return Response({'error': 'Not part of an organisation'}, status=status.HTTP_400_BAD_REQUEST)


class GetUsersFormatExcel(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        workbook = Workbook()
        sheet = workbook.active

        drop_down_options = [f"{branch_obj.branch_name} ({branch_obj.id})" for branch_obj in  Branch.objects.filter(organisation = request.user.organisation)]
        # Define column headers
        headers = ["First Name", "Last Name", "Email", "Date Of Birth", "Branch", "Phone", "Gender", "Education", "Experience"]

        # Add headers to the first row of the sheet
        sheet.append(headers)

        # Define drop-down options for the "Location" column
        drop_down_gender_options = ["Male", "Female", "Other"]

        # Create a DataValidation object for the drop-down list
        data_validation = DataValidation(type="list", formula1=f'"{",".join(drop_down_options)}"', allow_blank=False, showDropDown=False)
        data_validation.error ='Your entry is not in the list'
        data_validation.errorTitle = 'Invalid Entry'
        data_validation.prompt = 'Please select from the list'
        data_validation.promptTitle = 'List Selection'
        data_validation.add('E2:E1048576')
        gender_data_validation = DataValidation(type="list", formula1=f'"{",".join(drop_down_gender_options)}"', allow_blank=False, showDropDown=False)
        gender_data_validation.error ='Your entry is not in the list'
        gender_data_validation.errorTitle = 'Invalid Entry'
        gender_data_validation.prompt = 'Please select from the list'
        gender_data_validation.promptTitle = 'List Selection'
        gender_data_validation.add('G2:G1048576')
        # Apply the data validation to a specific range (e.g., D2:D1048576)
        sheet.add_data_validation(data_validation)
        sheet.add_data_validation(gender_data_validation)
        # data_validation.add(sheet["B2:D1048576"])
        

        # Create a response with the Excel file
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = "attachment; filename=sample_excel_with_dropdown.xlsx"

        # Save the workbook to the response
        workbook.save(response)

        return response

class BranchBroadcastHistoryView(APIView):

    def get(self, request):

        branch_broadcast_history_objs = BranchBroadcastHistory.objects.filter(organisation = request.user.organisation)

        serializer_obj = BranchBroadcastHistorySerializer(branch_broadcast_history_objs, many = True)

        return Response({
            "status": 200,
            'message': 'Records found',
            'data': serializer_obj.data
            })