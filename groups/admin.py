from django.contrib import admin
from .models import Group, GroupMembership


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    readonly_fields = ['joined_at']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'creator__user_id', 'creator__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [GroupMembershipInline]

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['group', 'user', 'added_by', 'joined_at']
    list_filter = ['joined_at']
    search_fields = ['group__name', 'user__user_id', 'user__email']
