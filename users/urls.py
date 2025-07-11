from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='user-register'),
    path('login/', views.login, name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('search/', views.search_users, name='user-search'),
    path('by-id/<str:user_id>/', views.get_user_by_id, name='user-by-id'),
]
