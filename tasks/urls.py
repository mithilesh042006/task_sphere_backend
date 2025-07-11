from django.urls import path
from . import views

urlpatterns = [
    # Task management
    path('', views.TaskListView.as_view(), name='task-list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('groups/<int:group_id>/create/', views.TaskCreateView.as_view(), name='task-create'),
    
    # Task swaps
    path('swaps/', views.TaskSwapListView.as_view(), name='task-swap-list'),
    path('<int:task_id>/swap/', views.create_task_swap, name='task-swap-create'),
    path('swaps/<int:swap_id>/approve-admin/', views.approve_swap_admin, name='task-swap-approve-admin'),
    path('swaps/<int:swap_id>/approve-user/', views.approve_swap_user, name='task-swap-approve-user'),
    path('swaps/<int:swap_id>/reject/', views.reject_swap, name='task-swap-reject'),
]
