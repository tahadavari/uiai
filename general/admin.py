from django.contrib import admin
from general.models import *
# Register your models here.
@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    exclude = ['hash']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    exclude = ['hash']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    exclude = ['hash']

@admin.register(EmailNews)
class EmailNewsAdmin(admin.ModelAdmin):
    exclude = ['hash']


@admin.register(Social)
class SocialAdmin(admin.ModelAdmin):
    exclude = ['hash']

