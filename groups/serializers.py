from rest_framework import serializers
from .models import Group, GroupMembership
from users.serializers import UserSearchSerializer


class GroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for group membership"""
    user = UserSearchSerializer(read_only=True)
    added_by = UserSearchSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = ['user', 'added_by', 'joined_at']


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for group details"""
    creator = UserSearchSerializer(read_only=True)
    members = UserSearchSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'creator', 'members', 'member_count', 
                 'is_admin', 'created_at', 'updated_at']
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_is_admin(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_admin(request.user)
        return False


class GroupCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating groups"""
    class Meta:
        model = Group
        fields = ['name', 'description']
    
    def create(self, validated_data):
        request = self.context['request']
        group = Group.objects.create(creator=request.user, **validated_data)
        # Add creator as member
        group.add_member(request.user)
        return group


class GroupListSerializer(serializers.ModelSerializer):
    """Serializer for group list view"""
    creator = UserSearchSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'creator', 'member_count', 'is_admin', 'created_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_is_admin(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_admin(request.user)
        return False


class AddMemberSerializer(serializers.Serializer):
    """Serializer for adding members to group"""
    user_id = serializers.CharField(max_length=8)
    
    def validate_user_id(self, value):
        from users.models import User
        try:
            user = User.objects.get(user_id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this ID does not exist")
