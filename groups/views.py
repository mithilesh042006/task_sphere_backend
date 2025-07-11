from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Group, GroupMembership
from .serializers import (
    GroupSerializer,
    GroupCreateSerializer,
    GroupListSerializer,
    AddMemberSerializer,
    GroupMembershipSerializer
)


class GroupListCreateView(generics.ListCreateAPIView):
    """List user's groups and create new groups"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupCreateSerializer
        return GroupListSerializer

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Group detail, update, and delete"""
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user)

    def perform_update(self, serializer):
        # Only group admin can update
        group = self.get_object()
        if not group.is_admin(self.request.user):
            raise permissions.PermissionDenied("Only group admin can update group")
        serializer.save()

    def perform_destroy(self, instance):
        # Only group admin can delete
        if not instance.is_admin(self.request.user):
            raise permissions.PermissionDenied("Only group admin can delete group")
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_member(request, group_id):
    """Add member to group by user ID"""
    group = get_object_or_404(Group, id=group_id, members=request.user)

    # Check if user is admin
    if not group.is_admin(request.user):
        return Response({'error': 'Only group admin can add members'},
                       status=status.HTTP_403_FORBIDDEN)

    serializer = AddMemberSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user_id']

        # Check if user is already a member
        if group.members.filter(id=user.id).exists():
            return Response({'error': 'User is already a member'},
                           status=status.HTTP_400_BAD_REQUEST)

        membership, created = group.add_member(user, request.user)
        if created:
            return Response({'message': f'User {user.user_id} added successfully'})
        else:
            return Response({'error': 'User is already a member'},
                           status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_member(request, group_id, user_id):
    """Remove member from group"""
    group = get_object_or_404(Group, id=group_id, members=request.user)

    # Check if user is admin
    if not group.is_admin(request.user):
        return Response({'error': 'Only group admin can remove members'},
                       status=status.HTTP_403_FORBIDDEN)

    try:
        from users.models import User
        user = User.objects.get(user_id=user_id)

        # Cannot remove the creator
        if user == group.creator:
            return Response({'error': 'Cannot remove group creator'},
                           status=status.HTTP_400_BAD_REQUEST)

        # Check if user is a member
        if not group.members.filter(id=user.id).exists():
            return Response({'error': 'User is not a member'},
                           status=status.HTTP_400_BAD_REQUEST)

        group.remove_member(user)
        return Response({'message': f'User {user.user_id} removed successfully'})

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def group_members(request, group_id):
    """Get group members"""
    group = get_object_or_404(Group, id=group_id, members=request.user)
    memberships = GroupMembership.objects.filter(group=group)
    serializer = GroupMembershipSerializer(memberships, many=True)
    return Response(serializer.data)
