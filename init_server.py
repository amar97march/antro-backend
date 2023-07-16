from profiles.serializers import ProfileSerializer
from profiles.models import Profile, Keyword
from django.contrib.gis.geos import fromstr
from profiles.models import ProfileCategory, ProfileCategorySocialSite
import random
from users.models import User
from faker import Faker
fake = Faker()

platforms = [
    {"name": "Facebook", "category": "Social Networking"},
    {"name": "Twitter", "category": "Social Networking"},
    {"name": "Instagram", "category": "Social Networking"},
    {"name": "LinkedIn", "category": "Social Networking"},
    {"name": "Snapchat", "category": "Social Networking"},
    {"name": "Pinterest", "category": "Social Networking"},
    {"name": "Reddit", "category": "Social Networking"},
    {"name": "Tumblr", "category": "Social Networking"},
    {"name": "TikTok", "category": "Social Networking"},
    {"name": "YouTube", "category": "Video Sharing"},
    {"name": "WhatsApp", "category": "Messaging"},
    {"name": "WeChat", "category": "Messaging"},
    {"name": "Line", "category": "Messaging"},
    {"name": "Telegram", "category": "Messaging"},
    {"name": "VKontakte (VK)", "category": "Social Networking"},
    {"name": "Sina Weibo", "category": "Social Networking"},
    {"name": "Qzone", "category": "Social Networking"},
    {"name": "Weibo", "category": "Social Networking"},
    {"name": "Xing", "category": "Social Networking"},
    {"name": "Meetup", "category": "Event Management"},
    {"name": "Flickr", "category": "Photo Sharing"},
    {"name": "Badoo", "category": "Social Networking"},
    {"name": "MySpace", "category": "Social Networking"},
    {"name": "SoundCloud", "category": "Music Streaming"},
    {"name": "Twitch", "category": "Video Sharing"},
    {"name": "Medium", "category": "Blogging"},
    {"name": "Quora", "category": "Question and Answer"},
    {"name": "Yelp", "category": "Review and Recommendation"},
    {"name": "Foursquare", "category": "Location-Based"},
    {"name": "Vine", "category": "Video Sharing"},
    {"name": "WordPress", "category": "Blogging"},
    {"name": "Blogger", "category": "Blogging"},
    {"name": "500px", "category": "Photo Sharing"},
    {"name": "Vimeo", "category": "Video Sharing"},
    {"name": "Dailymotion", "category": "Video Sharing"},
    {"name": "Zoom", "category": "Video Conferencing"},
    {"name": "Microsoft Teams", "category": "Video Conferencing"},
    {"name": "Google Meet", "category": "Video Conferencing"},
    {"name": "Cisco Webex", "category": "Video Conferencing"},
    {"name": "Spotify", "category": "Music Streaming"},
    {"name": "Apple Music", "category": "Music Streaming"},
    {"name": "Airbnb", "category": "Travel and Accommodation"},
    {"name": "Booking.com", "category": "Travel and Accommodation"},
    {"name": "Expedia", "category": "Travel and Accommodation"},
    {"name": "Steam", "category": "Gaming"},
    {"name": "PlayStation Network", "category": "Gaming"},
    {"name": "Xbox Live", "category": "Gaming"},
    {"name": "Uber", "category": "Ride-Sharing"},
    {"name": "Lyft", "category": "Ride-Sharing"},
    {"name": "Tinder", "category": "Dating"},
    {"name": "Bumble", "category": "Dating"},
    {"name": "OkCupid", "category": "Dating"},
    {"name": "Google News", "category": "News Aggregation"},
    {"name": "Flipboard", "category": "News Aggregation"},
    {"name": "Apple News", "category": "News Aggregation"},
    {"name": "Dropbox", "category": "File Sharing and Cloud Storage"},
    {"name": "Google Drive", "category": "File Sharing and Cloud Storage"},
    {"name": "OneDrive", "category": "File Sharing and Cloud Storage"},
    {"name": "Apple Podcasts", "category": "Podcast"},
    {"name": "Spotify", "category": "Podcast"},
    {"name": "Google Podcasts", "category": "Podcast"},
    {"name": "Quora", "category": "Question and Answer"},
    {"name": "Stack Overflow", "category": "Question and Answer"},
    {"name": "Yahoo Answers", "category": "Question and Answer"},
    {"name": "Eventbrite", "category": "Event Management"},
    {"name": "Meetup", "category": "Event Management"},
    {"name": "PayPal", "category": "Payment Gateways"},
    {"name": "Stripe", "category": "Payment Gateways"},
    {"name": "Square", "category": "Payment Gateways"},
    {"name": "Ethereum", "category": "Blockchain"},
    {"name": "Binance Smart Chain", "category": "Blockchain"},
    {"name": "Cardano", "category": "Blockchain"},
    {"name": "GitHub", "category": "Open-Source Development"},
    {"name": "GitLab", "category": "Open-Source Development"},
    {"name": "Bitbucket", "category": "Open-Source Development"},
    {"name": "Oculus", "category": "Virtual Reality"},
    {"name": "HTC Vive", "category": "Virtual Reality"},
    {"name": "ARCore", "category": "Augmented Reality"},
    {"name": "ARKit", "category": "Augmented Reality"},
    {"name": "TensorFlow", "category": "Artificial Intelligence"},
    {"name": "PyTorch", "category": "Artificial Intelligence"},
    {"name": "IBM Watson", "category": "Artificial Intelligence"}
]


for item in platforms:
    cat, flag_cat = ProfileCategory.objects.get_or_create(
        name=item['category'])
    social, flag = ProfileCategorySocialSite.objects.get_or_create(
        name=item['name'], profile_category=cat)

cat, flag_cat = ProfileCategory.objects.get_or_create(name="Other")
for item in ProfileCategory.objects.all():
    social, flag = ProfileCategorySocialSite.objects.get_or_create(
        name="Other", profile_category=item)


user_list = list(User.objects.all())
profile_social_list = list(ProfileCategorySocialSite.objects.all())

for profile in range(0, 100):
    social_site_obj = random.choice(profile_social_list)
    print(social_site_obj.id, "==",  social_site_obj.profile_category.id)
    location_obj = fake.location_on_land()
    data = {
        "name": fake.name(),
        "company_name": fake.company(),
        "address": fake.address(),
        "city": fake.city(),
        "profession": fake.job(),
        "category": social_site_obj.profile_category.id,
        "social_site": social_site_obj.id,
        "location": {
            "latitude": location_obj[0],
            "longitude": location_obj[1]
        },
        "keywords": [
            fake.job(),
            fake.job(),
            fake.job()
        ]
    }
    data["user"] = random.choice(user_list).id
    # print(data)
    keywords = []
    for item in data['keywords']:
        # print(item)
        keyword_obj, created = Keyword.objects.get_or_create(name=item)
        keywords.append(keyword_obj.id)
    # print(keywords)
    data['keywords'] = keywords
    longitude = data['location']['longitude']
    latitude = data['location']['latitude']
    location = fromstr(f'POINT({longitude} {latitude})', srid=4326)
    data['location'] = location
    profile_serializer_obj = ProfileSerializer(data=data)
    if profile_serializer_obj.is_valid():
        profile_serializer_obj.save()
    else:
        print("Error: ", profile_serializer_obj.errors)
