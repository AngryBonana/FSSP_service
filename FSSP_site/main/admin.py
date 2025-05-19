from django.contrib import admin
from .models import SiteText

@admin.register(SiteText)
class SiteTextAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated')
    search_fields = ('name', 'content')