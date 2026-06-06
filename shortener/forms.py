from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ShortURL, generate_short_key
from django.utils import timezone

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ShortURLForm(forms.ModelForm):
    custom_key_input = forms.CharField(
        max_length=50, required=False,
        label='Custom short key (optional)',
        help_text='Leave blank for auto-generated key. Letters, numbers, hyphens only.'
    )
    expires_in = forms.ChoiceField(
        choices=[
            ('', 'Never'),
            ('1h', '1 Hour'),
            ('24h', '24 Hours'),
            ('7d', '7 Days'),
            ('30d', '30 Days'),
        ],
        required=False,
        label='Expiration'
    )

    class Meta:
        model = ShortURL
        fields = ['original_url', 'title']

    def clean_custom_key_input(self):
        key = self.cleaned_data.get('custom_key_input', '').strip()
        if not key:
            return key
        import re
        if not re.match(r'^[a-zA-Z0-9\-]+$', key):
            raise forms.ValidationError('Only letters, numbers, and hyphens allowed.')
        if ShortURL.objects.filter(short_key=key).exists():
            raise forms.ValidationError('This short key is already taken.')
        return key

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user

        custom = self.cleaned_data.get('custom_key_input')
        if custom:
            instance.short_key = custom
            instance.custom_key = True
        else:
            key = generate_short_key()
            while ShortURL.objects.filter(short_key=key).exists():
                key = generate_short_key()
            instance.short_key = key

        expires_in = self.cleaned_data.get('expires_in')
        if expires_in:
            from datetime import timedelta
            delta_map = {'1h': timedelta(hours=1), '24h': timedelta(hours=24),
                         '7d': timedelta(days=7), '30d': timedelta(days=30)}
            instance.expires_at = timezone.now() + delta_map[expires_in]

        if commit:
            instance.save()
        return instance

class EditURLForm(forms.ModelForm):
    class Meta:
        model = ShortURL
        fields = ['original_url', 'title', 'is_active']
