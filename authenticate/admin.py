from django.contrib import admin
from authenticate.models import ForgetPasswordEmailToken
# Register your models here.
@admin.register(ForgetPasswordEmailToken)
class ForgetPasswordEmailTokenAdmin(admin.ModelAdmin):
    exclude = ['hash']