# Human Resource Management (HRM) System using Django REST Framework

A comprehensive Human Resource Management (HRM) System REST API built with Django and Django REST Framework. This system provides complete employee lifecycle management including attendance tracking, leave management, supervisory oversight, and organizational hierarchy management.

---

## Features

### Employee Management
- Complete employee profile management with personal and professional details
- Department and designation hierarchy
- Supervisor-employee relationship mapping
- Employee status tracking (active, inactive, resigned)
- RFID-based employee identification
- Educational and employment history tracking

### Attendance Management
- Real-time attendance marking with timezone support (Asia/Dhaka)
- Shift-based attendance tracking with flexible in/out times
- Automated late arrival and early departure calculations
- Attendance adjustments and approval workflows
- Monthly and daily attendance summaries and analytics
- Employee attendance history under per supervisor 
- RFID integration for seamless check-in/check-out

### Leave Management
- Comprehensive leave request system
- Multiple leave types configuration
- Leave balance tracking and management
- Multi-level approval workflows
- Leave transfer between employees
- Leave group management for different employee categories

### Authentication & Authorization
- Employee ID-based authentication system
- Role-based access control (Employee/Supervisor/Admin)

### Reporting & Analytics
- Employee performance dashboards
- Supervisor team management interface
- Monthly attendance reports with detailed analytics
- Late arrival and early departure tracking
- Department-wise attendance summaries

### Organizational Structure
- Department management
- Designation hierarchy
- Location-based employee tracking
- Office timing configurations
- Shift preference management

---

## Technologies Used

- **Backend**: Python 3.12, Django 5.2.1
- **API Framework**: Django REST Framework 3.16.0
- **Database**: SQLite (Development), PostgreSQL (Production Ready)
- **Timezone**: PyTZ, ZoneInfo for Asia/Dhaka timezone
- **Filtering**: django-filter for advanced API filtering
- **Documentation**: Markdown support for browsable API

---

## Prerequisites

- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Ishrakul-Tahmid/Human-Resource-Management-HRM-System-using-Django-REST-Framework.git
```

### 2. Create and activate virtual environment

**Windows:**
```bash
python -m venv hrm_env
.\hrm_env\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv hrm_env
source hrm_env/bin/activate
```

### 3. Install dependencies

```bash
pip install djangorestframework
pip install django-filter
pip install markdown
```

### 4. Configure settings

Update your `settings.py` with the following configuration:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'users',
    'leave_management',
    'employee',
    'attendence',
]

# Timezone Configuration
TIME_ZONE = 'Asia/Dhaka'
USE_TZ = True

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
```

### 5. Database setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run development server

```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

---

## API Endpoints

### Employee Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/employee/employees/` | List employees |
| GET/PUT/DELETE | `/employee/employees/{employee_id}/` | Employee details operations |

### Attendance Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/attendance/api/attendance/` | Attendance records |
| GET/POST | `/attendance/api/shift-in-out/` | Shift management |
| GET | `/attendance/employee/employee_id{id}/Month_serial{month}/` | Employee monthly summary |
| GET | `/attendance/supervisor/{supervisor_id}/{month}/` | Team monthly summary |
| GET | `/attendance/supervisor/{supervisor_id}/` | Team daily summary |

### Leave Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/leave/api/leave-requests/` | Leave requests |
| GET/POST | `/leave/api/leave-types/` | Leave types management |
| GET/POST | `/leave/api/leave-approvals/` | Leave approvals |

---

## Project Structure

```
CompanyHR/
├── leave/                      # Main project configuration
│   ├── settings.py            # Django settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
├── employee/                  # Employee management app
│   ├── models.py             # Employee, Department, Designation models
│   ├── serializers.py        # Employee API serializers
│   ├── views.py              # Employee API views
│   └── urls.py               # Employee routes
├── attendence/               # Attendance management app
│   ├── models.py             # Attendance, ShiftInOut models
│   ├── serializers.py        # Attendance serializers with timezone
│   ├── views.py              # Attendance API and analytics views
│   ├── urls.py               # Attendance routes
│   └── utils.py              # Time calculation utilities
├── leave_management/         # Leave system app
│   ├── models.py             # Leave types, requests, approvals
│   ├── serializers.py        # Leave management serializers
│   ├── views.py              # Leave API views
│   └── urls.py               # Leave routes
├── authentication/           # Authentication app
│   ├── models.py             # Custom employee user model
│   ├── views.py              # Auth and quick attendance views
│   └── urls.py               # Authentication routes
└── users/                    # User management utilities
```

---

## Key Features Explained

### Timezone Intelligence
Automatic timezone conversion ensures all attendance records are accurately stored in UTC while displaying in Asia/Dhaka timezone for local operations.

### Smart Attendance Analytics
- **Late Calculation**: Automatic late time calculation with configurable grace periods
- **Early Departure**: Tracks early leaving with supervisor notifications
- **Monthly Insights**: Comprehensive monthly reports for performance reviews

### Supervisor Dashboard
Supervisors can access:
- Real-time team attendance status
- Monthly team performance analytics
- Leave approval queues
- Team productivity metrics

### Leave Workflow Engine
- Multi-stage approval process
- Automatic leave balance management
- Leave conflict detection
- Emergency leave handling

---

## Usage Examples

### Supervisor Analytics
```bash
# Get team monthly summary
curl http://127.0.0.1:8000/attendance/supervisor/EMP001/08/

# Get today's team attendance
curl http://127.0.0.1:8000/attendance/supervisor/EMP001/
```

---

## Security Features

- **Data Validation**: Comprehensive input validation and sanitization
- **Audit Trail**: Complete tracking of all system activities

---

## Business Benefits

### For HR Department
- Streamlined employee onboarding and management
- Automated attendance and leave tracking
- Comprehensive reporting and analytics
- Reduced manual paperwork

### For Supervisors
- Real-time team visibility
- Easy approval workflows
- Performance tracking tools
- Team productivity insights

### For Employees
- Self-service attendance marking
- Easy leave request submission
- Personal attendance history
- Mobile-friendly interface

---

## 🔧 Admin Panel

Access the comprehensive admin interface at:
```
http://127.0.0.1:8000/admin/
```

**Admin Features:**
- Complete employee database management
- System configuration and settings
- Attendance and leave oversight
- Report generation and analytics
- User role and permission management

---

## Scalability & Performance

- **Database Optimization**: Efficient queries with proper indexing
- **API Caching**: Response caching for improved performance
- **Modular Architecture**: Easy to extend and customize
- **Production Ready**: Configured for deployment scaling

---

