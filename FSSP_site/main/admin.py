from django.contrib import admin
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'is_active', 'order')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)