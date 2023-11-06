import requests
import random
from rest_framework_simplejwt.tokens import RefreshToken
import os
from antrobackend.settings import env
from email.message import EmailMessage
import smtplib


EMAIL_ADDRESS = 'amar97march@gmail.com'
EMAIL_PASSWORD = 'moxppjlxvbrypsnl'

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



def send_notification(emails, type, data):

    msg = EmailMessage()

    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ["amar97march@gmail.com"] #emails

    if type == "new_onboard":
        msg['Subject'] = 'You are invited to antro'
        msg.set_content(f'''
            <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            margin: 0;
                            padding: 0;
                        }}

                        .container {{
                            max-width: 800px;
                            margin: 0 auto;
                            padding: 20px;
                            background-color: #ffffff;
                        }}
                        .container .inner-container {{
                            background: #f5f7f9;
                            box-shadow: rgba(100, 100, 111, 0.2) 0px 7px 29px 0px;
                            margin: 5%;
                            padding: 20px;
                            border-radius: 5px;
                        }}

                        h1 {{
                            color: #333;
                        }}

                        p {{
                            font-size: 16px;
                            line-height: 1.6;
                            color: #555;
                        }}

                        .button {{
                            display: inline-block;
                            padding: 10px 20px;
                            background-color: #0076f4;
                            color: #fff;
                            text-decoration: none;
                            border-radius: 5px;
                        }}

                        .button:hover {{
                            background-color: #0056b3;
                        }}
                        .link-btn {{
                            padding: 10px 15px;
                            border: none;
                            border-radius: 20px;
                            background: #0076ff;
                            color: white;
                            margin: auto;
                        }}

                        .footer {{
                            margin-top: 20px;
                            font-size: 14px;
                            color: #777;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Welcome to Antro</h1>
                        <div class="inner-container">
                        <p>Dear {data["receiver_name"]},</p>
                        <p>Please follow this link to move further.</p>
                        <div style="text-align: center;">
                            <a href="{data["link"]}"><button class="link-btn">Learn More</button></a>
                        </div>
                        <p>Thank you</p>
                        <p>Best regards,</p>
                        <p>Team Antro</p>
                        </div>
                        <p class="footer">This email is sent to you as part of our publication process. Please do not reply to this email. If you have any questions, please contact our support team.</p>
                    </div>
                </body>
                </html>
            ''', subtype='html')
        

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("Email Sent")
        smtp.send_message(msg)
