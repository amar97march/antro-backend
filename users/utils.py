import requests
import random
from rest_framework_simplejwt.tokens import RefreshToken
import os
from antrobackend.settings import env

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def send_verification_otp(phone_number):

    try:
        # print(env("2FACTOR_API_KEY"))
        print("ASFASFG: ", env('TWO_FACTOR_API_KEY'), phone_number)
        otp = random.randint(100000, 999999)
        url = f'https://2factor.in/API/V1/{env("TWO_FACTOR_API_KEY")}/SMS/{phone_number}/{otp}/OTP1'
        response = requests.get(url)
        print("Send OTP: ", response.json())
        return otp
    
    except Exception as e:
        print(e)
        return None
