from django.db import models
from django.conf import settings


class Notification(models.Model):
    """Notification model for task assignments, swaps, and reminders"""

    NOTIFICATION_TYPES = [
        ('task_assigned', 'Task Assigned'),
        ('task_updated', 'Task Updated'),
        ('swap_requested', 'Swap Requested'),
        ('swap_approved', 'Swap Approved'),
        ('swap_rejected', 'Swap Rejected'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('group_invitation', 'Group Invitation'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Optional references to related objects
    related_task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_swap = models.ForeignKey(
        'tasks.TaskSwap',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.user_id}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    @classmethod
    def create_task_assigned(cls, task, recipient):
        """Create notification for task assignment"""
        return cls.objects.create(
            recipient=recipient,
            notification_type='task_assigned',
            title=f'New task assigned: {task.title}',
            message=f'You have been assigned a new task: {task.title}',
            related_task=task,
            related_group=task.group
        )

    @classmethod
    def create_swap_request(cls, swap_request):
        """Create notification for swap request"""
        return cls.objects.create(
            recipient=swap_request.target_user,
            notification_type='swap_requested',
            title=f'Task swap request: {swap_request.task.title}',
            message=f'{swap_request.requester.first_name} wants to swap task: {swap_request.task.title}',
            related_task=swap_request.task,
            related_swap=swap_request
        )

    @classmethod
    def create_swap_approved(cls, swap_request):
        """Create notification for approved swap"""
        return cls.objects.create(
            recipient=swap_request.requester,
            notification_type='swap_approved',
            title=f'Swap approved: {swap_request.task.title}',
            message=f'Your swap request for {swap_request.task.title} has been approved',
            related_task=swap_request.task,
            related_swap=swap_request
        )
