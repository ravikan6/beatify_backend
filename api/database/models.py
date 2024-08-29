from mongoengine import *

class User(DynamicDocument):
    first_name = StringField(max_length=200, required=True)
    last_name = StringField(max_length=200, required=True)
    middle_name: StringField(max_length=200, required=False)
    email_address = StringField(required=True)
    phone_number = StringField(max_length=15, required=True)

# # Create a new page and add tags
# >>> page = Page(title='Using MongoEngine')
# >>> page.tags = ['mongodb', 'mongoengine']
# >>> page.save()

# >>> Page.objects(tags='mongoengine').count()
# >>> 1