from django.contrib.auth import get_user_model
from organisation.models import Group, Organisation, Location, Branch, BranchBroadcastHistory, GroupParticipants, BroadcastMessage
from rest_framework.views import APIView
from chat.models import Chat, Contact
from chat.views import get_user_contact
from .serializers import GroupSerializer, LocationSerializer, BranchSerializer, BranchBroadcastHistorySerializer
from users.serializers import UserSerializer, TempUserSerializer, TempUserStatusSerializer
from rest_framework.response import Response
from rest_framework import status
import openpyxl
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework.permissions import IsAuthenticated, AllowAny
from openpyxl.worksheet.datavalidation import DataValidation
from django.db.models import Q
from ..utils import broadcast_to_branches_by_list, is_admin_of_group_or_parent, get_messages_of_group_and_children
from users.models import TempUser, TempUserStatus
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
        serializer_data = GroupSerializer(group_list, many=True, context={'request': request})
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

class UpdatePermissions(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.get('data', [])
        group_id = request.data.get('group_id', None)
        group_obj = Group.objects.get(id = group_id)
        if not is_admin_of_group_or_parent(request.user, group_obj):
            return Response({'error': 'Not admin'}, status=status.HTTP_400_BAD_REQUEST)
        
        for participant in data:
            user = User.objects.filter(id = participant["id"]).first()
            if user:
                group_participant_obj = GroupParticipants.objects.get(group = group_obj, user = user)
                group_participant_obj.sender = participant["sender"]
                group_participant_obj.admin = participant["admin"]
                group_participant_obj.save()
        return Response({
            "status": 200,
            'message': 'Permission updated',
            })

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
    
    def delete(self, request):
        partipants_list = request.data.get('participants', [])
        group_id = request.data.get('group_id', None)
        group_obj = Group.objects.get(id = group_id)
        if not is_admin_of_group_or_parent(request.user, group_obj):
            return Response({'error': 'Not admin'}, status=status.HTTP_400_BAD_REQUEST)
        for participant_id in partipants_list:
            user = User.objects.get(id = participant_id)
            
            group_participant_obj = GroupParticipants.objects.filter(group = group_obj, user = user).first()
            if group_participant_obj:

                group_participant_obj.delete()
        return Response({
            "status": 200,
            'message': 'Participants removed',
            })
        

class MyGroup(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        group_list = request.user.broadcast_groups.all()
        for grou in group_list:
            print(grou.participants)
        serializer_data = GroupSerializer(group_list, many=True, context={'request': request})
        return Response({
            "status": 200,
            'message': 'Records found',
            'data': serializer_data.data
            })
    
class GroupDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):

        group_obj = Group.objects.get(id = group_id)
        serializer_data = GroupSerializer(group_obj, context={'request': request})
        return Response({
            "status": 200,
            'message': 'Records found',
            'data': serializer_data.data
            })
    
class UpdateGroupMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            message_id = request.data.get('message_id', None)
            group_id = request.data.get('group_id', None)
            content = request.data.get('content', None)

            message_list = get_messages_of_group_and_children(group_id, message_id)
            for message in message_list:
                message_obj = BroadcastMessage.objects.get(id = message.id)
                message_obj.content = content
                message_obj.edited = True
                message_obj.save()

            return Response({
                "status": 200,
                'message': 'Message Updated',
                })
        except Exception as e:
            print(e)
            return Response({'error': 'Not updated'}, status=status.HTTP_400_BAD_REQUEST)
    
class OrganisationMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            organistion_obj = Organisation.objects.get(id = request.user.organisation.id)
            sort_by = request.GET.get('sort_by', [])
            search_keyword = request.GET.get('search_keyword', '')

            # users_list = User.objects.filter(organisation = organistion_obj)
            # user_serializer_obj = UserSerializer(users_list, many=True)

            temp_user_list = TempUserStatus.objects.filter(organisation = organistion_obj, upload_status__in = ['pending', 'completed']).order_by('created_at')
            if search_keyword:
                temp_user_list = temp_user_list.filter(
                    Q(first_name__icontains=search_keyword) |
                    Q(last_name__icontains=search_keyword) |
                    Q(email__icontains=search_keyword)
                )

            # Sort users based on provided fields
            if sort_by:
                print(sort_by)
                sort_by_mapped = sort_by
                if (sort_by == 'name'):
                    sort_by_mapped = 'first_name'
                elif (sort_by == 'status'):
                    sort_by_mapped = 'upload_status'
                temp_user_list = temp_user_list.order_by(sort_by_mapped)
            
            
            temp_user_serializer_obj = TempUserStatusSerializer(temp_user_list, many=True)

            return Response({
                "members": temp_user_serializer_obj.data
            })
        
        except Exception as e:
            print(e)
            return Response({'error': 'Not part of an organisation'}, status=status.HTTP_400_BAD_REQUEST)

class FailedUploadMembers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            organistion_obj = Organisation.objects.get(id = request.user.organisation.id)

            temp_user_list = TempUserStatus.objects.filter(organisation = organistion_obj, upload_status__in = ['failed']).order_by('created_at')
            
            temp_user_serializer_obj = TempUserStatusSerializer(temp_user_list, many=True)

            return Response({
                "members": temp_user_serializer_obj.data
            })
        
        except Exception as e:
            print(e)
            return Response({'error': 'Not part of an organisation'}, status=status.HTTP_400_BAD_REQUEST)


class GetUsersFormatExcel(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):

        workbook = Workbook()
        sheet = workbook.active

        drop_down_options = [f"{branch_obj.branch_name} ({branch_obj.id})" for branch_obj in  Branch.objects.filter(organisation__id = id)]
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