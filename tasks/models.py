from django.db import models
from django.conf import settings
from groups.models import Group


class Task(models.Model):
    """Task model with individual and group assignment capabilities"""

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')
    deadline = models.DateTimeField(null=True, blank=True)

    # Task assignment - can be assigned to individual or group
    assigned_to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    assigned_to_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    # Task creator (group admin)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    # Group context (task belongs to this group)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def clean(self):
        """Ensure task is assigned to either user or group, not both"""
        from django.core.exceptions import ValidationError
        if self.assigned_to_user and self.assigned_to_group:
            raise ValidationError("Task cannot be assigned to both user and group")
        if not self.assigned_to_user and not self.assigned_to_group:
            raise ValidationError("Task must be assigned to either user or group")

    def is_assigned_to_user(self, user):
        """Check if task is assigned to specific user"""
        if self.assigned_to_user:
            return self.assigned_to_user == user
        elif self.assigned_to_group:
            return user in self.assigned_to_group.members.all()
        return False


class TaskSwap(models.Model):
    """Task swap model with approval workflow"""

    SWAP_STATUS_CHOICES = [
        ('pending_admin', 'Pending Admin'),
        ('pending_user', 'Pending User'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # The task being swapped (requester's task)
    requester_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='swap_requests_as_requester',
        help_text="Task that the requester wants to give away"
    )

    # The task that requester wants to receive
    target_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='swap_requests_as_target',
        help_text="Task that the requester wants to receive"
    )

    # Users involved in the swap
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='initiated_swaps'
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_swaps'
    )

    # Approval status
    status = models.CharField(max_length=15, choices=SWAP_STATUS_CHOICES, default='pending_admin')
    admin_approved = models.BooleanField(default=False)
    user_approved = models.BooleanField(default=False)

    # Approval timestamps
    admin_approved_at = models.DateTimeField(null=True, blank=True)
    user_approved_at = models.DateTimeField(null=True, blank=True)

    # Rejection reason
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        # unique_together = ['requester_task', 'target_task', 'requester']  # Temporarily disabled for migration

    def __str__(self):
        return f"Swap: {self.requester_task.title} ↔ {self.target_task.title} ({self.requester.user_id} ↔ {self.target_user.user_id})"

    def approve_by_admin(self, admin_user):
        """Approve swap by group admin"""
        if self.requester_task.group.is_admin(admin_user):
            from django.utils import timezone
            self.admin_approved = True
            self.admin_approved_at = timezone.now()
            self.update_status()
            self.save()
            return True
        return False

    def approve_by_user(self, user):
        """Approve swap by target user"""
        if user == self.target_user:
            from django.utils import timezone
            self.user_approved = True
            self.user_approved_at = timezone.now()
            self.update_status()
            self.save()
            return True
        return False

    def reject(self, reason=""):
        """Reject the swap request"""
        self.status = 'rejected'
        self.rejection_reason = reason
        self.save()

    def update_status(self):
        """Update status based on approvals"""
        if self.admin_approved and self.user_approved:
            self.status = 'approved'
            self.execute_swap()
        elif self.admin_approved and not self.user_approved:
            self.status = 'pending_user'
        elif not self.admin_approved:
            self.status = 'pending_admin'

    def execute_swap(self):
        """Execute the task swap by swapping assignments of both tasks"""
        if self.status == 'approved':
            # Store original assignments
            requester_task_user = self.requester_task.assigned_to_user
            target_task_user = self.target_task.assigned_to_user

            # Swap the assignments
            self.requester_task.assigned_to_user = target_task_user
            self.target_task.assigned_to_user = requester_task_user

            # Save both tasks
            self.requester_task.save()
            self.target_task.save()
