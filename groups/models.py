from django.db import models
from django.conf import settings


class Group(models.Model):
    """Group model with creator-admin relationship"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_groups',
        help_text="User who created this group (becomes admin)"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='GroupMembership',
        through_fields=('group', 'user'),
        related_name='user_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_admin(self, user):
        """Check if user is admin (creator) of this group"""
        return self.creator == user

    def add_member(self, user, added_by=None):
        """Add a member to the group"""
        membership, created = GroupMembership.objects.get_or_create(
            group=self,
            user=user,
            defaults={'added_by': added_by or self.creator}
        )
        return membership, created

    def remove_member(self, user):
        """Remove a member from the group"""
        GroupMembership.objects.filter(group=self, user=user).delete()


class GroupMembership(models.Model):
    """Through model for Group-User relationship"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_memberships'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['group', 'user']
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.user_id} in {self.group.name}"
