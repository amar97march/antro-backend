from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # Use Q objects to search for either email or user_id
        user = UserModel.objects.filter(Q(email=username) | Q(user_id=username)).first()

        if user and user.check_password(password):
            return user
        return None