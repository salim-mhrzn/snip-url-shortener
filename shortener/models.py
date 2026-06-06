from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string, random

BASE62_CHARS = string.ascii_letters + string.digits

def generate_short_key(length=7):
    return ''.join(random.choices(BASE62_CHARS, k=length))

class ShortURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='short_urls')
    original_url = models.URLField(max_length=2000)
    short_key = models.CharField(max_length=50, unique=True, db_index=True)
    custom_key = models.BooleanField(default=False)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    click_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.short_key} -> {self.original_url[:50]}"

    def is_expired(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    def is_valid(self):
        return self.is_active and not self.is_expired()

class ClickEvent(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    referer = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['-clicked_at']
