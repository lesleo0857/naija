from django.contrib import admin

# Register your models here.
from hosting.models import *

admin.site.register(Checkoutt),
admin.site.register(Category),
admin.site.register(Brand),
admin.site.register(Section),
admin.site.register(Products),
admin.site.register(Payment),
admin.site.register(Customer),
admin.site.register(Order),
admin.site.register(OrderItem),
admin.site.register(Subject),
admin.site.register(Student),
admin.site.register(Student_subject),

