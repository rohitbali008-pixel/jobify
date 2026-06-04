from django.contrib import admin
from .models import User , Profile , Company , Employee , Job, Application ,Category, Question

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(Employee)
admin.site.register(Job)
admin.site.register(Application)
admin.site.register(Category)
admin.site.register(Question)