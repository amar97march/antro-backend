import time
import requests
import random
from rest_framework_simplejwt.tokens import RefreshToken
import os
from antrobackend.settings import env
from django.conf import settings
from email.message import EmailMessage
import smtplib
import secrets
import string
import boto3
from users.models import UserProfile, AuthenticationEntity
from django.core.files.storage import FileSystemStorage
from celery import shared_task
from moviepy.editor import VideoFileClip



EMAIL_ADDRESS = 'amar97march@gmail.com'
EMAIL_PASSWORD = 'moxppjlxvbrypsnl'

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def send_verification_otp(phone_number, otp):

    try:
        url = f'https://2factor.in/API/V1/{env("TWO_FACTOR_API_KEY")}/SMS/{phone_number}/{otp}/OTP1'
        response = requests.get(url)
        print("Send OTP: ", response.json())
        return otp
    
    except Exception as e:
        print(e)
        return None
    
def send_reset_password_otp(email, otp):
    try:
        email_data = {
            "otp": otp
        }
        send_notification([email], "reset_password", email_data)
    
    except Exception as e:
        print(e)
        return None

    
def send_email_verification_otp(email, otp):

    try:
        email_data = {
            "otp": otp
        }
        send_notification([email], "email_verification", email_data)

    
    except Exception as e:
        print(e)
        return None
    

def send_email_account_merge_otp(email, otp):

    try:
        email_data = {
            "otp": otp
        }
        send_notification([email], "account_merge_otp", email_data)

    
    except Exception as e:
        print(e)
        return None



def send_notification(emails, type, data):

    msg = EmailMessage()

    msg['From'] = ["amar97march@gmail.com"] # EMAIL_ADDRESS
    msg['To'] = emails

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
        
    if type == "email_verification":
        msg['Subject'] = 'Antro Email Verification'
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
                        <p>Hi</p>
                        <p>Please use the following 6 digit number to verify your account.</p>
                        <div style="text-align: center;">
                            {data['otp']}
                        </div>
                        <p>Thank you</p>
                        <p>Best regards,</p>
                        <p>Team Antro</p>
                        </div>
                    </div>
                </body>
                </html>
            ''', subtype='html')
        
    if type == "account_merge_otp":
        msg['Subject'] = 'Antro Account Merge'
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
                        <p>Hi</p>
                        <p>Please use the following 6 digit number to verify your account.</p>
                        <div style="text-align: center;">
                            {data['otp']}
                        </div>
                        <p>Thank you</p>
                        <p>Best regards,</p>
                        <p>Team Antro</p>
                        </div>
                    </div>
                </body>
                </html>
            ''', subtype='html')
        
    if type == "reset_password":
        msg['Subject'] = 'Antro: Reset Password'
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
                        <h1>Reset Password</h1>
                        <div class="inner-container">
                        <p>Hi</p>
                        <p>Please use the following 6 digit number to reset your account password.</p>
                        <div style="text-align: center;">
                            {data['otp']}
                        </div>
                        <p>Thank you</p>
                        <p>Best regards,</p>
                        <p>Team Antro</p>
                        </div>
                    </div>
                </body>
                </html>
            ''', subtype='html')
        

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("Email Sent")
        smtp.send_message(msg)


def generate_random_string(length=15):
    alphanumeric_characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(alphanumeric_characters) for _ in range(length))
    return random_string
import re

import multiprocessing

def compare_selfie_with_all_users(image, first_name, last_name, date_of_birth, authentication_entity_id, transcribed_data, detected_gesture, image_url):

    print("AMAR AT 42")
    authentication_entity_obj = AuthenticationEntity.objects.get(id = authentication_entity_id)
    rekognition = boto3.client('rekognition',
                               aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                               region_name='ap-south-1')

    # response = requests.get(selfie_image_url)  # Fetch the selfie image from the URL
    selfie_image_bytes = image #.read()  # Get the image content as bytes

    # with open('selfie_image.jpg', 'wb') as selfie_image_file:  # Save the image temporarily (optional)
    #     selfie_image_file.write(selfie_image_bytes)

    try:
        authentication_entity_obj.status = AuthenticationEntity.Status.Failed
        for user in UserProfile.objects.all():
            if (user.image):
                # user_picture_path = user.image.path
                # user_picture_relative_path = user.image.url
                
                response = rekognition.compare_faces(
                    SourceImage={'Bytes': selfie_image_bytes},  # Use the fetched bytes
                    TargetImage={'Bytes': user.image.read()}
                )
                print(response['FaceMatches'], transcribed_data["otp"], detected_gesture)
                if response['FaceMatches'] and user.user.first_name == first_name and user.user.last_name == last_name and str(user.user.date_of_birth) == date_of_birth:
                    if (re.search(str(authentication_entity_obj.otp), transcribed_data["otp"]) and authentication_entity_obj.gesture == detected_gesture):
                        
                        authentication_entity_obj.first_name = first_name
                        authentication_entity_obj.last_name = last_name
                        authentication_entity_obj.date_of_birth = date_of_birth
                        authentication_entity_obj.image_url = image_url
                        
                        AuthenticationEntity.objects.filter(user = user.user).delete()
                        authentication_entity_obj.user = user.user
                        authentication_entity_obj.status = AuthenticationEntity.Status.Verified
                            
                        authentication_entity_obj.save()
                        break
        
        authentication_entity_obj.save()
    except Exception as e:
        print(e)

    finally:
        if os.path.exists('selfie_image.jpg'):  # Delete the temporary image (if saved)
            os.remove('selfie_image.jpg')

import io
import cv2
import mediapipe as mp
import numpy as np
import math

# mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
gestures = {
    "fist": {
        "fingertip_distances": [0.1, 0.2, 0.3, 0.4],  # Approximate distances for curled fingers
        "finger_angles": [60, 50, 40, 30],  # Approximate angles for tight bending
        "thumb_angle": 10  # Approximate angle for thumb tucked in
    },
    "open_hand": {
        "fingertip_distances": [0.8, 1.0, 1.2, 1.4],  # Approximate distances for extended fingers
        "finger_angles": [150, 160, 170, 180],  # Approximate angles for straight fingers
        "thumb_angle": 170  # Approximate angle for thumb extended
    },
    "thumbs_up": {
        "fingertip_distances": [0.8, 1.0, 1.2, 1.4],  # Similar to open hand for non-thumb fingers
        "finger_angles": [150, 160, 170, 180],  # Similar to open hand for non-thumb fingers
        "thumb_angle": 160  # Thumb extended upwards
    },
    "thumbs_down": {
        "fingertip_distances": [0.8, 1.0, 1.2, 1.4],  # Similar to open hand for non-thumb fingers
        "finger_angles": [150, 160, 170, 180],  # Similar to open hand for non-thumb fingers
        "thumb_angle": 30  # Thumb extended downwards
    }
    # Add more gestures as needed, including their relevant features
}

def initialize_hands():
    """Creates and initializes mp_hands.Hands object."""
    hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    return hands

def calculate_fingertip_distances(hand_landmarks):
    """Calculates approximate distances between fingertips and the palm center."""

    # Indices of fingertips (adjust based on MediaPipe's landmark model)
    fingertip_indices = [8, 12, 16, 20]  # Indices for index, middle, ring, and pinky fingers
    landmark_points = np.array([(landmark.x, landmark.y, landmark.z) for landmark in hand_landmarks.landmark[0:5]])
    palm_center = np.mean(landmark_points, axis=0)

    distances = []
    for fingertip_index in fingertip_indices:
        fingertip = hand_landmarks.landmark[fingertip_index]
        distance = np.linalg.norm(np.array(
            [fingertip.x - palm_center[0],
                          fingertip.y - palm_center[1],
                          fingertip.z - palm_center[2]]
                          ))
        distances.append(distance)

    return distances

def calculate_finger_angles(hand_landmarks):
    """Calculates approximate angles between finger joints."""

    # Indices of finger joints (adjust based on MediaPipe's landmark model)
    finger_joint_indices = [
        [5, 6, 8],  # Index finger
        [9, 10, 12],  # Middle finger
        [13, 14, 16],  # Ring finger
        [17, 18, 20]  # Pinky finger
    ]

    angles = []
    for finger_joints in finger_joint_indices:
        # Calculate angle using the law of cosines
        a = np.linalg.norm(np.array(
            [hand_landmarks.landmark[finger_joints[1]].x - hand_landmarks.landmark[finger_joints[0]].x,
                           hand_landmarks.landmark[finger_joints[1]].y - hand_landmarks.landmark[finger_joints[0]].y]))
        b = np.linalg.norm(np.array([hand_landmarks.landmark[finger_joints[2]].x - hand_landmarks.landmark[finger_joints[1]].x,
                           hand_landmarks.landmark[finger_joints[2]].y - hand_landmarks.landmark[finger_joints[1]].y]))
        c = np.linalg.norm(np.array([hand_landmarks.landmark[finger_joints[2]].x - hand_landmarks.landmark[finger_joints[0]].x,
                           hand_landmarks.landmark[finger_joints[2]].y - hand_landmarks.landmark[finger_joints[0]].y]))
        angle = math.degrees(math.acos((a**2 + b**2 - c**2) / (2 * a * b)))  # Convert from radians to degrees
        angles.append(angle)

    return angles

def calculate_thumb_angle(hand_landmarks):
    """Calculates the approximate angle of the thumb relative to the palm."""

    # Indices of thumb joints (adjust based on MediaPipe's landmark model)
    thumb_joint_indices = [2, 3, 4]  # Base, middle, and tip joints of the thumb

    # Calculate angle using the law of cosines
    a = np.linalg.norm(np.array(
            [hand_landmarks.landmark[thumb_joint_indices[1]].x - hand_landmarks.landmark[thumb_joint_indices[0]].x,
                       hand_landmarks.landmark[thumb_joint_indices[1]].y - hand_landmarks.landmark[thumb_joint_indices[0]].y]))
    b = np.linalg.norm(np.array(
            [hand_landmarks.landmark[thumb_joint_indices[2]].x - hand_landmarks.landmark[thumb_joint_indices[1]].x,
                       hand_landmarks.landmark[thumb_joint_indices[2]].y - hand_landmarks.landmark[thumb_joint_indices[1]].y]))
    c = np.linalg.norm(np.array(
            [hand_landmarks.landmark[thumb_joint_indices[2]].x - hand_landmarks.landmark[thumb_joint_indices[0]].x,
                       hand_landmarks.landmark[thumb_joint_indices[2]].y - hand_landmarks.landmark[thumb_joint_indices[0]].y]))
    angle = math.degrees(math.acos((a**2 + b**2 - c**2) / (2 * a * b)))  # Convert from radians to degrees

    return angle

def calculate_feature_distance(features1, features2):
    """Calculates a distance measure between two sets of gesture features."""

    total_distance = 0
    for feature_name, feature_value1 in features1.items():
        feature_value2 = features2.get(feature_name)  # Get the corresponding feature value from the second set
        if feature_value2 is not None:  # Ensure both sets have the feature
            if isinstance(feature_value1, list):  # Handle lists of values (e.g., fingertip distances)
                total_distance += np.linalg.norm(np.array(feature_value1) - np.array(feature_value2))  # Euclidean distance
            else:  # Handle single values (e.g., angles)
                total_distance += abs(feature_value1 - feature_value2)  # Absolute difference

    return total_distance

@shared_task
def classify_gesture(image_bytes):
    """Classifies a gesture from a single byte image."""

    # Decode the image bytes into a NumPy array
    image_array = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)

    # Initialize MediaPipe Hands only for this image
    print("yyy1")
    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        print("kkkkk65")
        results = hands.process(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
        print("kkkk67")

        # Extract hand landmarks if detected
        hand_landmarks = results.multi_hand_landmarks[0] if results.multi_hand_landmarks else None
        print("kkk69")
    # multiprocessing.current_process().daemon = False
    # with multiprocessing.Pool(processes=1) as pool:
    #     results = pool.apply(process_image, (image_array,))
    #     hand_landmarks = results[0]
    print("yyy2")
    # If landmarks are found, proceed with gesture classification
    if hand_landmarks:
        # Extract relevant features from the detected hand landmarks
        features = {
            "fingertip_distances": calculate_fingertip_distances(hand_landmarks),
            "finger_angles": calculate_finger_angles(hand_landmarks),
            "thumb_angle": calculate_thumb_angle(hand_landmarks),
            # ... (extract other relevant features)
        }
        print("yyy3")
        # Compare extracted features with predefined gesture features
        closest_gesture = None
        min_distance = float('inf')
        for gesture_name, gesture_features in gestures.items():
            distance = calculate_feature_distance(features, gesture_features)
            if distance < min_distance:
                min_distance = distance
                closest_gesture = gesture_name
        print("yyy4")
        return closest_gesture
    else:
        return "No hand detected"
    
def process_image(image_array):
    """Processes an image using MediaPipe Hands."""
    # Reconstruct AuthenticationString within the function (if needed)
    # ... (reconstruction logic using original creation method)

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:  # Use reconstructed object here
        results = hands.process(cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
        return results.multi_hand_landmarks[0] if results.multi_hand_landmarks else None

@shared_task
def transcribe_code_from_audio_wav(audio_filename, duration):
    """
    Transcribes code from an audio WAV file using AWS Transcribe service.

    Args:
        audio_filename (str): The name of the audio file to transcribe.
        duration (int): The duration of the audio file in seconds.

    Returns:
        dict: A dictionary containing the transcribed text and the URL of the audio file.
    """
    transcribe = boto3.client('transcribe',
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                               region_name='ap-south-1')
    job_name = f'transcribe_job_{audio_filename}{int(duration // 2)}{int(time.time())}'  # Unique job name
    
    # Save the video to S3
    local_storage = FileSystemStorage(location=os.path.join(settings.BASE_DIR,'staticfiles'))  # Adjust path as needed
    local_file_path = f'{os.path.join(settings.BASE_DIR, "staticfiles")}/{audio_filename}'
    s3_bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3_file_key = f'media/public/{audio_filename}'
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    try:
        s3.upload_file(local_file_path, s3_bucket_name, s3_file_key)
        print("File uploaded successfuddlly to S3")
    except Exception as e:
        print("Error uploading file:", e)
    job_uri = f"https://antro-backend.s3.ap-south-1.amazonaws.com/media/public/{audio_filename}"
    # job_uri = f"https://antro-backend.s3.ap-south-1.amazonaws.com/media/public/extracted_audioa_2.wav"
    print("amasf4223")
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='en-US'  # Adjust language code as needed
    )
    print("aksjfsa132412")

    # Wait for transcription job to complete
    while True:
        job_status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if job_status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        # time.sleep(5)  # Check status every 5 seconds
    print("kakakakskkakkikikikuku")
    
    # Retrieve transcribed text
    if job_status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcript = transcribe.get_transcription_job(TranscriptionJobName=job_name)['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript_text = requests.get(transcript).json()
        otp = transcript_text["results"]["transcripts"][0]["transcript"]
        file_path = local_storage.path(audio_filename)  # Get the full file path
        os.remove(file_path)
        print("gjkhjhjhkhjhj")
        return {"otp": otp}
    else:
        print("Transcription job failed:", job_status['TranscriptionJob']['FailureReason'])
        return {"otp": None}


