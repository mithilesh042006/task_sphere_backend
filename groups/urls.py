from django.urls import path
from . import views

urlpatterns = [
    path('', views.GroupListCreateView.as_view(), name='group-list-create'),
    path('<int:group_id>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('<int:group_id>/members/', views.group_members, name='group-members'),
    path('<int:group_id>/add-member/', views.add_member, name='group-add-member'),
    path('<int:group_id>/remove-member/<str:user_id>/', views.remove_member, name='group-remove-member'),
]
