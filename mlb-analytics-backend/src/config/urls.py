from django.contrib import admin
from django.urls import path, include
from apps.auth_views import login_view, register_view, logout_view
from apps.teams.views import standings_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/teams/', include('apps.teams.urls')),
    path('api/v1/players/', include('apps.players.urls')),
    path('api/v1/games/', include('apps.games.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/search/', include('search.urls')),
    path('api/v1/standings/', standings_view, name='standings'),
    path('api/auth/', include('rest_framework.urls')),
    
    # Custom authentication endpoints for React Native
    path('api/v1/auth/login/', login_view, name='login'),
    path('api/v1/auth/register/', register_view, name='register'),
    path('api/v1/auth/logout/', logout_view, name='logout'),
]