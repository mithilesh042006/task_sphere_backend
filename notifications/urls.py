from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='notification-read'),
    path('mark-all-read/', views.mark_all_read, name='notification-mark-all-read'),
    path('unread-count/', views.unread_count, name='notification-unread-count'),
]
