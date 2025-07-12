from rest_framework import serializers
from .models import Task, TaskSwap
from users.serializers import UserSearchSerializer
from groups.serializers import GroupListSerializer


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for task details"""
    assigned_to_user = UserSearchSerializer(read_only=True)
    assigned_to_group = GroupListSerializer(read_only=True)
    created_by = UserSearchSerializer(read_only=True)
    group = GroupListSerializer(read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_swap = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'priority', 'status', 'deadline',
                 'assigned_to_user', 'assigned_to_group', 'created_by', 'group',
                 'can_edit', 'can_swap', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'group', 'created_at', 'updated_at']
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.group.is_admin(request.user)
        return False
    
    def get_can_swap(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_assigned_to_user(request.user)
        return False


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    assigned_to_user_id = serializers.CharField(max_length=8, required=False, allow_blank=True)
    assign_to_group = serializers.BooleanField(default=False)
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'deadline', 'assigned_to_user_id', 'assign_to_group']
    
    def validate(self, attrs):
        assigned_to_user_id = attrs.get('assigned_to_user_id')
        assign_to_group = attrs.get('assign_to_group', False)
        
        if not assigned_to_user_id and not assign_to_group:
            raise serializers.ValidationError("Task must be assigned to either a user or the group")
        
        if assigned_to_user_id and assign_to_group:
            raise serializers.ValidationError("Task cannot be assigned to both user and group")
        
        return attrs
    
    def validate_assigned_to_user_id(self, value):
        if value:
            from users.models import User
            try:
                user = User.objects.get(user_id=value)
                # Check if user is member of the group (will be validated in view)
                return user
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this ID does not exist")
        return None


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'deadline']


class TaskSwapSerializer(serializers.ModelSerializer):
    """Serializer for task swap details"""
    requester_task = TaskSerializer(read_only=True)
    target_task = TaskSerializer(read_only=True)
    requester = UserSearchSerializer(read_only=True)
    target_user = UserSearchSerializer(read_only=True)
    can_approve_admin = serializers.SerializerMethodField()
    can_approve_user = serializers.SerializerMethodField()

    class Meta:
        model = TaskSwap
        fields = ['id', 'requester_task', 'target_task', 'requester', 'target_user', 'status',
                 'admin_approved', 'user_approved', 'admin_approved_at',
                 'user_approved_at', 'rejection_reason', 'can_approve_admin',
                 'can_approve_user', 'created_at', 'updated_at']
    
    def get_can_approve_admin(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.requester_task.group.is_admin(request.user) and not obj.admin_approved
        return False
    
    def get_can_approve_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.target_user == request.user and not obj.user_approved
        return False


class TaskSwapCreateSerializer(serializers.Serializer):
    """Serializer for creating task swap requests"""
    target_user_id = serializers.CharField(max_length=8)
    target_task_id = serializers.IntegerField()

    def validate_target_user_id(self, value):
        from users.models import User
        try:
            return User.objects.get(user_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this ID does not exist")

    def validate_target_task_id(self, value):
        try:
            return Task.objects.get(id=value)
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task with this ID does not exist")
