# TaskSphere Backend API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Test Users
- Admin: YUJ7IVR8 (admin@tasksphere.com) - password: admin123
- User 1: 4MTYP209 (john@example.com) - password: password123
- User 2: HBQ5M7Z8 (jane@example.com) - password: password123
- User 3: K90AL0AU (bob@example.com) - password: password123

## API Endpoints

### Authentication (`/api/auth/`)

#### Register User
```
POST /api/auth/register/
{
    "email": "user@example.com",
    "username": "username",
    "first_name": "First",
    "last_name": "Last",
    "password": "password123",
    "password_confirm": "password123"
}
```

#### Login
```
POST /api/auth/login/
{
    "email": "user@example.com",
    "password": "password123"
}
```

#### Refresh Token
```
POST /api/auth/token/refresh/
{
    "refresh": "refresh_token_here"
}
```

#### User Profile
```
GET /api/auth/profile/
PUT /api/auth/profile/
```

#### Search Users
```
GET /api/auth/search/?q=search_term
```

#### Get User by ID
```
GET /api/auth/by-id/<user_id>/
```

### Groups (`/api/groups/`)

#### List/Create Groups
```
GET /api/groups/
POST /api/groups/
{
    "name": "Group Name",
    "description": "Group description"
}
```

#### Group Details
```
GET /api/groups/<group_id>/
PUT /api/groups/<group_id>/
DELETE /api/groups/<group_id>/
```

#### Group Members
```
GET /api/groups/<group_id>/members/
```

#### Add Member
```
POST /api/groups/<group_id>/add-member/
{
    "user_id": "8DIGIT_ID"
}
```

#### Remove Member
```
DELETE /api/groups/<group_id>/remove-member/<user_id>/
```

### Tasks (`/api/tasks/`)

#### List Tasks
```
GET /api/tasks/
GET /api/tasks/?group=<group_id>
GET /api/tasks/?status=<status>
```

#### Task Details
```
GET /api/tasks/<task_id>/
PUT /api/tasks/<task_id>/
PATCH /api/tasks/<task_id>/
DELETE /api/tasks/<task_id>/
```

#### Create Task
```
POST /api/tasks/groups/<group_id>/create/
{
    "title": "Task Title",
    "description": "Task description",
    "priority": "high|medium|low|urgent",
    "deadline": "2024-12-31T23:59:59Z",
    "assigned_to_user_id": "8DIGIT_ID",  // OR
    "assign_to_group": true
}
```

#### Task Swaps
```
GET /api/tasks/swaps/
POST /api/tasks/<task_id>/swap/
{
    "target_user_id": "8DIGIT_ID"
}
```

#### Approve/Reject Swaps
```
POST /api/tasks/swaps/<swap_id>/approve-admin/
POST /api/tasks/swaps/<swap_id>/approve-user/
POST /api/tasks/swaps/<swap_id>/reject/
{
    "reason": "Optional rejection reason"
}
```

### Notifications (`/api/notifications/`)

#### List Notifications
```
GET /api/notifications/
```

#### Mark as Read
```
POST /api/notifications/<notification_id>/read/
POST /api/notifications/mark-all-read/
```

#### Unread Count
```
GET /api/notifications/unread-count/
```

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Task Status Options
- `not_started`: Not Started
- `in_progress`: In Progress
- `completed`: Completed
- `cancelled`: Cancelled

## Task Priority Options
- `low`: Low
- `medium`: Medium
- `high`: High
- `urgent`: Urgent

## Task Swap Status Options
- `pending_admin`: Pending Admin Approval
- `pending_user`: Pending User Approval
- `approved`: Approved
- `rejected`: Rejected
