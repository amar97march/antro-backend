from celery import shared_task
from moviepy.editor import VideoFileClip
import os
import boto3
import logging
from django.core.files.storage import FileSystemStorage
# from celery.signals import after_setup_logger
from django.conf import settings
from .utils import transcribe_code_from_audio_wav, classify_gesture, compare_selfie_with_all_users


# logger = logging.getLogger(__name__)
# logger.warning("this will get printed")

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
# @after_setup_logger.connect
# def setup_loggers(logger, *args, **kwargs):
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#     # add filehandler
#     fh = logging.FileHandler('logs.log')
#     fh.setLevel(logging.DEBUG)
#     fh.setFormatter(formatter)
#     logger.addHandler(fh)


@shared_task
def test(name):
    print(name)
    logger.info('doing task')
    logger.warning('doing task')


@shared_task
def perform_user_detection(filename, authentication_entity_id, first_name, last_name, date_of_birth):
    
    try:
        detected_gesture = None
        image_url = None
        image_bytes = None
        video_clip = VideoFileClip(f"staticfiles/{filename}")
        duration = video_clip.duration

        # Audio Extract
        logger.warning('Found addition')
        audio_clip = video_clip.audio
        audio_filename = f'extracted_audio_{authentication_entity_id}.wav'
        filename_full = os.path.join(settings.BASE_DIR,'staticfiles', audio_filename)
        audio_clip.write_audiofile(filename_full)
        transcribed_data =  transcribe_code_from_audio_wav(audio_filename, duration)
        print("KJghjg1")
        # Video frame
        image_filename = f'screenshot_{authentication_entity_id}.jpg'
        image_filename_full = os.path.join(settings.BASE_DIR,'staticfiles', image_filename)
        video_clip.save_frame(image_filename_full, t=duration // 2)
        print("KJghjg1.1")
        with open(image_filename_full, 'rb') as image_file:
            image_bytes = image_file.read()
            detected_gesture = classify_gesture(image_bytes)
        print("KJghjg2")
        local_storage = FileSystemStorage(location=os.path.join(settings.BASE_DIR,'staticfiles'))  # Adjust path as needed
        local_file_path = f'{os.path.join(settings.BASE_DIR, "staticfiles")}/{image_filename}'
        s3_bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        print("KJghjg3")
        s3_file_key = f'media/public/{image_filename}'
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        try:
            s3.upload_file(local_file_path, s3_bucket_name, s3_file_key)
            print("File uploaded successfully to S3-2")
        except Exception as e:
            print("Error uploading file:", e)
        image_url = f"https://antro-backend.s3.ap-south-1.amazonaws.com/media/public/{image_filename}"

        print("File uploaded dsafasf to S3")
    except Exception as e:
        print("User Validating Error: ", str(e))
    print("User Validating Error: ")
    file_path = local_storage.path(filename)  # Get the full file path
    os.remove(file_path)
    compare_selfie_with_all_users(image_bytes, first_name, last_name, date_of_birth, authentication_entity_id, transcribed_data, detected_gesture, image_url)
