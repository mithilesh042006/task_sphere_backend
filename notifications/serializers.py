from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 
                 'created_at', 'read_at', 'related_task', 'related_group', 'related_swap']
        read_only_fields = ['id', 'created_at', 'read_at']
