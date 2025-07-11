from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Task, TaskSwap
from groups.models import Group
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    TaskSwapSerializer,
    TaskSwapCreateSerializer
)


class TaskListView(generics.ListAPIView):
    """List tasks assigned to user"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        group_id = self.request.query_params.get('group')
        status_filter = self.request.query_params.get('status')

        # Base queryset - tasks assigned to user or groups user belongs to
        queryset = Task.objects.filter(
            Q(assigned_to_user=user) |
            Q(assigned_to_group__in=user.user_groups.all())
        ).distinct()

        # Filter by group if specified
        if group_id:
            queryset = queryset.filter(group_id=group_id)

        # Filter by status if specified
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class TaskCreateView(generics.CreateAPIView):
    """Create new task (group admin only)"""
    serializer_class = TaskCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        group_id = self.kwargs['group_id']
        group = get_object_or_404(Group, id=group_id, members=self.request.user)

        # Check if user is group admin
        if not group.is_admin(self.request.user):
            raise permissions.PermissionDenied("Only group admin can create tasks")

        # Get assignment details
        assigned_to_user_id = serializer.validated_data.get('assigned_to_user_id')
        assign_to_group = serializer.validated_data.get('assign_to_group', False)

        # Prepare task data
        task_data = {
            'title': serializer.validated_data['title'],
            'description': serializer.validated_data.get('description', ''),
            'priority': serializer.validated_data.get('priority', 'medium'),
            'deadline': serializer.validated_data.get('deadline'),
            'created_by': self.request.user,
            'group': group
        }

        if assign_to_group:
            task_data['assigned_to_group'] = group
        elif assigned_to_user_id:
            # Validate user is member of group
            if not group.members.filter(id=assigned_to_user_id.id).exists():
                raise serializers.ValidationError("User must be a member of the group")
            task_data['assigned_to_user'] = assigned_to_user_id

        task = Task.objects.create(**task_data)

        # Create notification for assigned user(s)
        from notifications.models import Notification
        if task.assigned_to_user:
            Notification.create_task_assigned(task, task.assigned_to_user)
        elif task.assigned_to_group:
            for member in task.assigned_to_group.members.all():
                if member != self.request.user:  # Don't notify the creator
                    Notification.create_task_assigned(task, member)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Task detail, update, and delete"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(assigned_to_user=user) |
            Q(assigned_to_group__in=user.user_groups.all()) |
            Q(group__creator=user)  # Include tasks in groups user administers
        ).distinct()

    def perform_update(self, serializer):
        task = self.get_object()
        # Only assigned users can update status, only group admin can update other fields
        if self.request.method == 'PATCH' and 'status' in serializer.validated_data:
            # User can update status if task is assigned to them
            if not task.is_assigned_to_user(self.request.user):
                raise permissions.PermissionDenied("You can only update status of tasks assigned to you")
        else:
            # Full update requires admin privileges
            if not task.group.is_admin(self.request.user):
                raise permissions.PermissionDenied("Only group admin can fully update tasks")

        serializer.save()

    def perform_destroy(self, instance):
        # Only group admin can delete
        if not instance.group.is_admin(self.request.user):
            raise permissions.PermissionDenied("Only group admin can delete tasks")
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_task_swap(request, task_id):
    """Create task swap request"""
    task = get_object_or_404(Task, id=task_id)

    # Check if user can swap this task (must be assigned to them)
    if not task.is_assigned_to_user(request.user):
        return Response({'error': 'You can only swap tasks assigned to you'},
                       status=status.HTTP_403_FORBIDDEN)

    serializer = TaskSwapCreateSerializer(data=request.data)
    if serializer.is_valid():
        target_user = serializer.validated_data['target_user_id']

        # Check if target user is in the same group
        if not task.group.members.filter(id=target_user.id).exists():
            return Response({'error': 'Target user must be a member of the same group'},
                           status=status.HTTP_400_BAD_REQUEST)

        # Check if swap already exists
        if TaskSwap.objects.filter(task=task, requester=request.user, target_user=target_user).exists():
            return Response({'error': 'Swap request already exists'},
                           status=status.HTTP_400_BAD_REQUEST)

        # Create swap request
        swap = TaskSwap.objects.create(
            task=task,
            requester=request.user,
            target_user=target_user
        )

        # Create notification
        from notifications.models import Notification
        Notification.create_swap_request(swap)

        return Response(TaskSwapSerializer(swap, context={'request': request}).data,
                       status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskSwapListView(generics.ListAPIView):
    """List task swap requests for user"""
    serializer_class = TaskSwapSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Show swaps where user is requester, target, or admin of the group
        return TaskSwap.objects.filter(
            Q(requester=user) |
            Q(target_user=user) |
            Q(task__group__creator=user)
        ).distinct()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_swap_admin(request, swap_id):
    """Approve task swap as group admin"""
    swap = get_object_or_404(TaskSwap, id=swap_id)

    if swap.approve_by_admin(request.user):
        # Create notification if fully approved
        if swap.status == 'approved':
            from notifications.models import Notification
            Notification.create_swap_approved(swap)

        return Response(TaskSwapSerializer(swap, context={'request': request}).data)
    else:
        return Response({'error': 'You are not authorized to approve this swap'},
                       status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_swap_user(request, swap_id):
    """Approve task swap as target user"""
    swap = get_object_or_404(TaskSwap, id=swap_id)

    if swap.approve_by_user(request.user):
        # Create notification if fully approved
        if swap.status == 'approved':
            from notifications.models import Notification
            Notification.create_swap_approved(swap)

        return Response(TaskSwapSerializer(swap, context={'request': request}).data)
    else:
        return Response({'error': 'You are not authorized to approve this swap'},
                       status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_swap(request, swap_id):
    """Reject task swap request"""
    swap = get_object_or_404(TaskSwap, id=swap_id)

    # Can be rejected by admin or target user
    if not (swap.task.group.is_admin(request.user) or swap.target_user == request.user):
        return Response({'error': 'You are not authorized to reject this swap'},
                       status=status.HTTP_403_FORBIDDEN)

    reason = request.data.get('reason', '')
    swap.reject(reason)

    return Response(TaskSwapSerializer(swap, context={'request': request}).data)
