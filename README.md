# Human Resource Management (HRM) System using Django REST Framework

A comprehensive Human Resource Management (HRM) System REST API built with Django and Django REST Framework. This system provides complete employee lifecycle management including attendance tracking, leave management, supervisory oversight, and organizational hierarchy management.

---

## Live Demo

**The system is live and accessible at:**
- **Main Application**: https://ishrakultahmid.pythonanywhere.com
- **Admin Panel**: https://ishrakultahmid.pythonanywhere.com/admin/
- **Employee API**: https://ishrakultahmid.pythonanywhere.com/employee/employees/
- **Attendance API**: https://ishrakultahmid.pythonanywhere.com/attendance/api/attendance/
- **Leave Management API**: https://ishrakultahmid.pythonanywhere.com/leave/api/leave-requests/

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
- **Database**: SQLite (Development), MySQL (Production on PythonAnywhere)
- **Authentication**: Token-based authentication
- **Timezone**: PyTZ, ZoneInfo for Asia/Dhaka timezone
- **Filtering**: django-filter for advanced API filtering
- **Documentation**: Markdown support for browsable API
- **Deployment**: PythonAnywhere (Free Tier)

---

## Prerequisites

- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

---

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ishrakul-Tahmid/Human-Resource-Management-HRM-System-using-Django-REST-Framework.git
cd Human-Resource-Management-HRM-System-using-Django-REST-Framework
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
pip install pytz
```

### 4. Configure settings

Update your `settings.py` for local development:

```python
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

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
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
```

### 5. Database setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser

```bash
python manage.py createsuperuser
```

### 7. Run development server

```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

---

## Production Deployment on PythonAnywhere

### 1. Create PythonAnywhere Account
Sign up at [pythonanywhere.com](https://www.pythonanywhere.com) and choose the **Free tier**.

### 2. Upload Your Project

**Git Clone Method (Recommended):**
```bash
# In PythonAnywhere console
cd ~
git clone https://github.com/Ishrakul-Tahmid/Human-Resource-Management-HRM-System-using-Django-REST-Framework.git
mv Human-Resource-Management-HRM-System-using-Django-REST-Framework leave
cd leave
```

### 3. Install Dependencies
```bash
pip3.10 install --user djangorestframework django-filter markdown pytz
```

### 4. Configure Production Settings

Edit `leave/settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/static/'

# Database for production (SQLite works fine for small-medium projects)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 5. Database Setup
```bash
cd ~/leave
python3.10 manage.py makemigrations
python3.10 manage.py migrate
python3.10 manage.py collectstatic --noinput
python3.10 manage.py createsuperuser
```

### 6. Create Web App

1. **Web** tab → **Add a new web app**
2. **Manual configuration** → **Python 3.10**
3. Set paths:
   - **Source code**: `/home/yourusername/leave`
   - **Working directory**: `/home/yourusername/leave`

### 7. Configure WSGI

Edit WSGI configuration file:
```python
import os
import sys

path = '/home/yourusername/leave'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'leave.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 8. Static Files Setup

**Web** tab → **Static files**:
- URL: `/static/`
- Directory: `/home/yourusername/static/`

### 9. Reload and Test

1. Click **"Reload"** button
2. Visit: `https://yourusername.pythonanywhere.com`

---

## Complete API Documentation

### Employee Management APIs

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/employee/employees/` | List all employees | Get all employees list |
| POST | `/employee/employees/` | Create new employee | Add new employee |
| GET | `/employee/employees/{employee_id}/` | Get specific employee | `/employee/employees/21-45402-3/` |
| PUT | `/employee/employees/{employee_id}/` | Update employee (full) | Update all employee fields |
| PATCH | `/employee/employees/{employee_id}/` | Update employee (partial) | Update specific fields |
| DELETE | `/employee/employees/{employee_id}/` | Delete employee | Remove employee |

**Employee API Examples:**

```bash
# Get all employees
GET https://ishrakultahmid.pythonanywhere.com/employee/employees/

# Get specific employee
GET https://ishrakultahmid.pythonanywhere.com/employee/employees/EMP001/

# Create new employee
POST https://ishrakultahmid.pythonanywhere.com/employee/employees/
{
    "employee_id": "EMP002",
    "employee_name": "John Doe",
    "email_id": "john@company.com",
    "department": 1,
    "designation": 1,
    "joining_date": "2024-01-15",
    "status": "active"
}
```

### Department & Designation APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/employee/departments/` | List/Create departments |
| GET/PUT/DELETE | `/employee/departments/{id}/` | Department operations |
| GET/POST | `/employee/designations/` | List/Create designations |
| GET/PUT/DELETE | `/employee/designations/{id}/` | Designation operations |
| GET/POST | `/employee/branches/` | List/Create branches |
| GET/PUT/DELETE | `/employee/branches/{id}/` | Branch operations |

### Attendance Management APIs

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/attendance/api/attendance/` | List attendance records | Get all attendance |
| POST | `/attendance/api/attendance/` | Create attendance record | Mark attendance |
| GET/POST | `/attendance/api/shift-in-out/` | Manage shift timings | Shift management |
| GET | `/attendance/api/attendance-summary/` | Attendance summaries | Monthly/daily summaries |
| GET | `/attendance/employee/employee_id{id}/Month_serial{month}/` | Employee monthly summary | `/attendance/employee/employee_idEMP001/Month_serial08/` |
| GET | `/attendance/supervisor/{supervisor_id}/{month}/` | Team monthly summary | `/attendance/supervisor/EMP001/08/` |
| GET | `/attendance/supervisor/{supervisor_id}/` | Team daily summary | `/attendance/supervisor/EMP001/` |

**Attendance API Examples:**

```bash
# Get all attendance records
GET https://ishrakultahmid.pythonanywhere.com/attendance/api/attendance/

# Create attendance record
POST https://ishrakultahmid.pythonanywhere.com/attendance/api/attendance/
{
    "employee": 1,
    "date": "2024-08-09",
    "status": "present",
    "in_time": "09:00:00",
    "out_time": "18:00:00"
}

# Get employee monthly summary
GET https://ishrakultahmid.pythonanywhere.com/attendance/employee/employee_idEMP001/Month_serial08/

# Get supervisor team summary
GET https://ishrakultahmid.pythonanywhere.com/attendance/supervisor/EMP001/08/
```

### Leave Management APIs

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/leave/api/leave-requests/` | List leave requests | Get all leave requests |
| POST | `/leave/api/leave-requests/` | Create leave request | Submit new leave request |
| GET/PUT/DELETE | `/leave/api/leave-requests/{id}/` | Leave request operations | Manage specific leave |
| GET/POST | `/leave/api/leave-types/` | Manage leave types | Sick, casual, annual leave |
| GET/POST | `/leave/api/leave-approvals/` | Handle leave approvals | Approve/reject leaves |
| GET/POST | `/leave/api/leave-balances/` | Leave balance management | Check remaining leaves |

**Leave Management API Examples:**

```bash
# Get all leave requests
GET https://ishrakultahmid.pythonanywhere.com/leave/api/leave-requests/

# Create leave request
POST https://ishrakultahmid.pythonanywhere.com/leave/api/leave-requests/
{
    "employee": 1,
    "leave_type": 1,
    "start_date": "2024-08-15",
    "end_date": "2024-08-17",
    "reason": "Family vacation",
    "status": "pending"
}

# Get leave types
GET https://ishrakultahmid.pythonanywhere.com/leave/api/leave-types/

# Approve leave request
PUT https://ishrakultahmid.pythonanywhere.com/leave/api/leave-requests/1/
{
    "status": "approved",
    "approved_by": 2
}
```

---

## Project Structure

```
HRM-System/
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
├── users/                    # User management utilities
└── db.sqlite3               # Database file
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

## Usage Examples with Live URLs

### Employee Management
```bash
# Create new employee via HTML form
https://ishrakultahmid.pythonanywhere.com/employee/employees/

# Get employee by ID
curl https://ishrakultahmid.pythonanywhere.com/employee/employees/EMP001/

# Update employee
curl -X PUT https://ishrakultahmid.pythonanywhere.com/employee/employees/EMP001/ \
  -H "Content-Type: application/json" \
  -d '{"employee_name": "Updated Name"}'
```

### Attendance Tracking
```bash
# Mark attendance
curl -X POST https://ishrakultahmid.pythonanywhere.com/attendance/api/attendance/ \
  -H "Content-Type: application/json" \
  -d '{"employee": 1, "date": "2024-08-09", "status": "present"}'

# Get monthly attendance summary
curl https://ishrakultahmid.pythonanywhere.com/attendance/employee/employee_idEMP001/Month_serial08/
```

### Leave Management
```bash
# Submit leave request
curl -X POST https://ishrakultahmid.pythonanywhere.com/leave/api/leave-requests/ \
  -H "Content-Type: application/json" \
  -d '{"employee": 1, "leave_type": 1, "start_date": "2024-08-15", "end_date": "2024-08-17"}'

# Get all leave requests
curl https://ishrakultahmid.pythonanywhere.com/leave/api/leave-requests/
```

---

## Security Features

- **Data Validation**: Comprehensive input validation and sanitization
- **Audit Trail**: Complete tracking of all system activities
- **HTTPS Encryption**: All data transmitted securely via HTTPS

---

## Business Benefits

### For HR Department
- Streamlined employee onboarding and management
- Automated attendance and leave tracking
- Comprehensive reporting and analytics
- Reduced manual paperwork
- Real-time access to employee data

### For Supervisors
- Real-time team visibility
- Easy approval workflows
- Performance tracking tools
- Team productivity insights
- Mobile-accessible dashboard

### For Employees
- Self-service attendance marking
- Easy leave request submission
- Personal attendance history
- Leave balance tracking
- Mobile-friendly interface

---

## Admin Panel Features

Access the comprehensive admin interface at:
```
https://ishrakultahmid.pythonanywhere.com/admin/
```

**Admin Features:**
- Complete employee database management
- System configuration and settings
- Attendance and leave oversight
- Report generation and analytics
- User role and permission management
- Department and designation management

---

## Scalability & Performance

- **Database Optimization**: Efficient queries with proper indexing
- **API Caching**: Response caching for improved performance
- **Modular Architecture**: Easy to extend and customize
- **Production Ready**: Deployed and tested on PythonAnywhere
- **Mobile Responsive**: Works on all device sizes

---

## Troubleshooting & Support

### Common Issues:

1. **API Access Issues**
   - Ensure correct URL format
   - Check HTTP methods (GET, POST, PUT, DELETE)
   - Verify request headers and data format

2. **Authentication Problems**
   - Use proper token authentication for protected endpoints
   - Check user permissions and roles

3. **Data Validation Errors**
   - Follow API documentation for required fields
   - Ensure proper data types and formats

### Getting Help:
- Check the browsable API documentation at any endpoint
- Use Django admin panel for data verification
- Review error logs through PythonAnywhere console

---



**Live System**: https://ishrakultahmid.pythonanywhere.com