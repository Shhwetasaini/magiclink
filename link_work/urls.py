from django.contrib import admin
from django.urls import path
from .views import LoginView, MagicLinkAuthView,RegisterView,UserDetailsView,LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/magic-link/<uuid:token>/', MagicLinkAuthView.as_view(), name='magic-link-auth'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', UserDetailsView.as_view(), name='user-details'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]
