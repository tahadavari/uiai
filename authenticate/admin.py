from django.contrib import admin
from uiai.authenticate.models import ForgetPasswordEmailToken
# Register your models here.
@admin.register(ForgetPasswordEmailToken)
class SettingAdmin(admin.ModelAdmin):
    exclude = ['hash']