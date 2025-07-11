from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from groups.models import Group
from tasks.models import Task
from notifications.models import Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Create test data for TaskSphere'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...')
        
        # Create test users
        admin_user = self.create_user(
            'admin@tasksphere.com', 'admin', 'Admin', 'User', 'admin123'
        )
        
        user1 = self.create_user(
            'john@example.com', 'john', 'John', 'Doe', 'password123'
        )
        
        user2 = self.create_user(
            'jane@example.com', 'jane', 'Jane', 'Smith', 'password123'
        )
        
        user3 = self.create_user(
            'bob@example.com', 'bob', 'Bob', 'Johnson', 'password123'
        )
        
        # Create test groups
        dev_group = Group.objects.create(
            name='Development Team',
            description='Software development team',
            creator=admin_user
        )
        dev_group.add_member(admin_user)
        dev_group.add_member(user1, admin_user)
        dev_group.add_member(user2, admin_user)
        
        marketing_group = Group.objects.create(
            name='Marketing Team',
            description='Marketing and promotion team',
            creator=user1
        )
        marketing_group.add_member(user1)
        marketing_group.add_member(user3, user1)
        
        # Create test tasks
        Task.objects.create(
            title='Implement user authentication',
            description='Create login and registration functionality',
            priority='high',
            assigned_to_user=user1,
            created_by=admin_user,
            group=dev_group
        )
        
        Task.objects.create(
            title='Design database schema',
            description='Create ERD and database design',
            priority='medium',
            assigned_to_user=user2,
            created_by=admin_user,
            group=dev_group
        )
        
        Task.objects.create(
            title='Create marketing campaign',
            description='Develop social media marketing strategy',
            priority='medium',
            assigned_to_group=marketing_group,
            created_by=user1,
            group=marketing_group
        )
        
        self.stdout.write(
            self.style.SUCCESS('Test data created successfully!')
        )
        self.stdout.write(f'Admin user: {admin_user.user_id} (admin@tasksphere.com)')
        self.stdout.write(f'User 1: {user1.user_id} (john@example.com)')
        self.stdout.write(f'User 2: {user2.user_id} (jane@example.com)')
        self.stdout.write(f'User 3: {user3.user_id} (bob@example.com)')

    def create_user(self, email, username, first_name, last_name, password):
        user = User.objects.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        # Generate user_id if not set
        if not user.user_id:
            from users.models import generate_user_id
            user.user_id = generate_user_id()
            user.save()
        
        self.stdout.write(f'Created user: {user.user_id} ({email})')
        return user
