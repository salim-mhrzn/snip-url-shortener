from django.contrib import admin
from .models import ShortURL, ClickEvent

@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ['short_key', 'user', 'original_url', 'click_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'custom_key']
    search_fields = ['short_key', 'original_url', 'user__username']

@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ['short_url', 'clicked_at', 'ip_address']
    list_filter = ['clicked_at']
