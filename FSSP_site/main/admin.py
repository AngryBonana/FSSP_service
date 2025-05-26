from django.contrib import admin
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'external_id', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content', 'external_id')
    readonly_fields = ('created_at', 'created_by')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'is_active', 'order')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)