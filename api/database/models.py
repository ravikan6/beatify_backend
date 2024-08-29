from mongoengine import *
import datetime
from nanoid import generate


class User(DynamicDocument):
    id = StringField(primary_key=True, required=True, default=generate(size=20))
    first_name = StringField(max_length=200, required=True)
    last_name = StringField(max_length=200, required=True)
    middle_name: StringField(max_length=200)
    email_address = EmailField(required=True, unique=True)
    phone_number = StringField(max_length=15)
    profile_picture = StringField()
    date_of_birth = DateTimeField()
    date_joined = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)
    password = StringField(required=True)