from django.contrib import admin
from .models import User , Profile , Company , Employee , Jobs, Application

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(Jobs)
admin.site.register(Application)