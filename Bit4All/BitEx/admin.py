from django.contrib import admin
from .models import Profile 

admin.site.register(Profile)

'''
    i know that when a new profile is created and the wallet field
    is assigned to a dict (as a mongodb embedded field shoudl), the profile
    cannot be correctly seen in the admin panel as im trying to show a dict 
    in the place of a model (class dict does not have Meta attribute)

    is this OK?
    
    answer : https://www.djongomapper.com/using-django-with-mongodb-data-fields/#using-embeddedfield-in-django-admin
'''