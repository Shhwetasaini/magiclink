from django.contrib import admin
from django.urls import path
from .views import LoginView, MagicLinkAuthView,RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/magic-link/<uuid:token>/', MagicLinkAuthView.as_view(), name='magic-link-auth'),
    path('auth/register/', RegisterView.as_view(), name='register'),
]
