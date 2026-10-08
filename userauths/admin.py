from django.contrib import admin
from userauths.models import User , ContactUs
# from import_export.admin import 
class USERAdmin(admin.ModelAdmin):
    list_display = ['username','email','bio']

admin.site.register(User,USERAdmin)

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['name','email','subject','message']

admin.site.register(ContactUs,ContactUsAdmin)