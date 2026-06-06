from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import ShortURL, ClickEvent
from .forms import RegisterForm, ShortURLForm, EditURLForm


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def dashboard(request):
    urls = ShortURL.objects.filter(user=request.user)
    total_urls = urls.count()
    total_clicks = sum(u.click_count for u in urls)
    recent_clicks = ClickEvent.objects.filter(
        short_url__user=request.user,
        clicked_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    return render(request, 'dashboard.html', {
        'urls': urls,
        'total_urls': total_urls,
        'total_clicks': total_clicks,
        'recent_clicks': recent_clicks,
    })


@login_required
def create_url(request):
    if request.method == 'POST':
        form = ShortURLForm(request.POST)
        if form.is_valid():
            url = form.save(user=request.user)
            messages.success(request, 'Short URL created successfully!')
            return redirect('url_detail', pk=url.pk)
    else:
        form = ShortURLForm()
    return render(request, 'create_url.html', {'form': form})


@login_required
def url_detail(request, pk):
    url = get_object_or_404(ShortURL, pk=pk, user=request.user)
    recent_clicks = url.clicks.filter(clicked_at__gte=timezone.now() - timedelta(days=30))
    short_url_full = request.build_absolute_uri(f'/{url.short_key}/')

    return render(request, 'url_detail.html', {
        'url': url,
        'short_url_full': short_url_full,
        'recent_clicks': recent_clicks[:10],
    })

@login_required
def edit_url(request, pk):
    url = get_object_or_404(ShortURL, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EditURLForm(request.POST, instance=url)
        if form.is_valid():
            form.save()
            messages.success(request, 'URL updated successfully!')
            return redirect('url_detail', pk=url.pk)
    else:
        form = EditURLForm(instance=url)
    return render(request, 'edit_url.html', {'form': form, 'url': url})


@login_required
def delete_url(request, pk):
    url = get_object_or_404(ShortURL, pk=pk, user=request.user)
    if request.method == 'POST':
        url.delete()
        messages.success(request, 'Short URL deleted.')
        return redirect('dashboard')
    return render(request, 'delete_url.html', {'url': url})


def redirect_view(request, short_key):
    url = get_object_or_404(ShortURL, short_key=short_key)
    if not url.is_valid():
        raise Http404('This URL is inactive or has expired.')
    # Record click
    ClickEvent.objects.create(
        short_url=url,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        referer=request.META.get('HTTP_REFERER', '')[:500],
    )
    url.click_count += 1
    url.save(update_fields=['click_count'])
    return redirect(url.original_url)