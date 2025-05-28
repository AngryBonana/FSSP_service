from django.contrib import admin
from .models import Card, FilterDate

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'parsed_date')
    list_editable = ('is_active', 'order', 'parsed_date')
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


@admin.register(FilterDate)
class FilterDateAdmin(admin.ModelAdmin):
    list_display = ('filter_date', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'filter_date')
    date_hierarchy = 'filter_date'

    fieldsets = (
        (None, {
            'fields': ('filter_date', 'is_active')
        }),
    )
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if obj.is_active:
            # Деактивируем все другие даты
            FilterDate.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)
