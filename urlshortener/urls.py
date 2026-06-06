from django.contrib import admin
from django.urls import path
from shortener import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_url, name='create_url'),
    path('url/<int:pk>/', views.url_detail, name='url_detail'),
    path('url/<int:pk>/edit/', views.edit_url, name='edit_url'),
    path('url/<int:pk>/delete/', views.delete_url, name='delete_url'),
    path('<str:short_key>/', views.redirect_view, name='redirect'),
]
