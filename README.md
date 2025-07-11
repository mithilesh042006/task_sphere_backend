# TaskSphere Backend

A Django REST API backend for the TaskSphere collaborative task management system.

## Features

- **User Management**: Custom user model with unique 8-digit alphanumeric IDs
- **Group-Based Ownership**: Users who create groups become admins automatically
- **Task Management**: Create, assign, and track tasks with individual or group assignment
- **Task Swapping**: Two-step approval process (admin + target user)
- **Notifications**: Real-time notifications for task assignments, swaps, and updates
- **JWT Authentication**: Secure token-based authentication
- **REST API**: Complete RESTful API with proper status codes and error handling

## Technology Stack

- **Framework**: Django 5.2 with Django REST Framework
- **Database**: SQLite (development) - easily configurable for PostgreSQL/MySQL
- **Authentication**: JWT tokens with refresh capability
- **API Documentation**: Comprehensive endpoint documentation

## Quick Start

### 1. Install Dependencies
```bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Test Data
```bash
python manage.py create_test_data
```

### 4. Start Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## Test Users

The `create_test_data` command creates the following test users:

- **Admin**: YUJ7IVR8 (admin@tasksphere.com) - password: admin123
- **User 1**: 4MTYP209 (john@example.com) - password: password123  
- **User 2**: HBQ5M7Z8 (jane@example.com) - password: password123
- **User 3**: K90AL0AU (bob@example.com) - password: password123

## API Documentation

See `API_DOCUMENTATION.md` for complete API endpoint documentation.

## Project Structure

```
task_sphere_backend/
├── users/              # User management and authentication
├── groups/             # Group management and membership
├── tasks/              # Task management and swapping
├── notifications/      # Notification system
├── task_sphere_backend/  # Main project settings
└── manage.py           # Django management script
```

## Key Models

### User
- Custom user model extending AbstractUser
- Unique 8-digit alphanumeric ID generation
- Email-based authentication

### Group
- Creator becomes admin automatically
- Many-to-many relationship with users
- Admin privileges for task management

### Task
- Flexible assignment (individual or group)
- Priority levels and status tracking
- Deadline management

### TaskSwap
- Two-step approval workflow
- Status tracking (pending_admin, pending_user, approved, rejected)
- Automatic task reassignment on approval

### Notification
- Multiple notification types
- Read/unread status tracking
- Related object references

## Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to manage:
- Users and their 8-digit IDs
- Groups and memberships
- Tasks and assignments
- Task swap requests
- Notifications

## Development Notes

- The server runs on port 8000 by default
- CORS is configured for frontend development
- JWT tokens expire after 1 hour (configurable)
- All API endpoints require authentication except registration and login
- Comprehensive error handling with proper HTTP status codes

## Next Steps

1. **Frontend Integration**: Connect with React/Vue.js frontend
2. **Real-time Features**: Add WebSocket support for live notifications
3. **File Attachments**: Add file upload capability for tasks
4. **Email Notifications**: Integrate email service for important notifications
5. **Production Deployment**: Configure for production with PostgreSQL and proper security settings
