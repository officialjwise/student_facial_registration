# KNUST Student Registration and Recognition System - Project Structure

```
knust_student_system/
│
├── api/
│   ├── __init__.py
│   ├── dependencies.py          # Dependency injection (DB, auth)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py          # Student registration and recognition endpoints
│   │   ├── admin.py             # Admin CRUD and stats endpoints
│   │   ├── auth.py              # Admin authentication and OTP endpoints
│   │   ├── colleges.py          # College CRUD endpoints
│   │   └── departments.py       # Department CRUD endpoints
│
├── core/
│   ├── __init__.py
│   ├── config.py                # Environment variables and settings
│   ├── security.py              # JWT and password hashing
│   └── email.py                 # Email OTP sending logic
│
├── crud/
│   ├── __init__.py
│   ├── students.py              # Student CRUD operations
│   ├── recognition_logs.py      # Recognition log operations
│   ├── colleges.py              # College CRUD operations
│   ├── departments.py           # Department CRUD operations
│   └── admin_users.py           # Admin user CRUD operations
│
├── models/
│   ├── __init__.py
│   ├── database.py              # Supabase client setup
│   ├── students.py              # Student database model
│   ├── recognition_logs.py      # Recognition log database model
│   ├── colleges.py              # College database model
│   ├── departments.py           # Department database model
│   └── admin_users.py           # Admin user database model
│
├── schemas/
│   ├── __init__.py
│   ├── students.py              # Pydantic schemas for students
│   ├── recognition_logs.py      # Pydantic schemas for recognition logs
│   ├── colleges.py              # Pydantic schemas for colleges
│   ├── departments.py           # Pydantic schemas for departments
│   ├── admin_users.py           # Pydantic schemas for admin users
│   └── auth.py                  # Pydantic schemas for authentication
│
├── services/
│   ├── __init__.py
│   ├── face_recognition.py      # Facial recognition logic
│   ├── students.py              # Student service logic
│   ├── recognition_logs.py      # Recognition log service logic
│   └── auth.py                  # Authentication and OTP service logic
│
├── tests/
│   ├── __init__.py
│   ├── test_students.py         # Tests for student endpoints
│   ├── test_auth.py             # Tests for authentication endpoints
│   ├── test_admin.py            # Tests for admin endpoints
│   ├── test_colleges.py         # Tests for college endpoints
│   └── test_departments.py      # Tests for department endpoints
│
├── main.py                      # FastAPI app entry point
├── requirements.txt             # Project dependencies
└── .env                         # Environment variables
```

## Terminal Command to Create Project Structure

```bash
mkdir -p knust_student_system/{api/routers,core,crud,models,schemas,services,tests} && touch knust_student_system/{main.py,requirements.txt,.env} && touch knust_student_system/api/{__init__.py,dependencies.py} && touch knust_student_system/api/routers/{__init__.py,students.py,admin.py,auth.py,colleges.py,departments.py} && touch knust_student_system/core/{__init__.py,config.py,security.py,email.py} && touch knust_student_system/crud/{__init__.py,students.py,recognition_logs.py,colleges.py,departments.py,admin_users.py} && touch knust_student_system/models/{__init__.py,database.py,students.py,recognition_logs.py,colleges.py,departments.py,admin_users.py} && touch knust_student_system/schemas/{__init__.py,students.py,recognition_logs.py,colleges.py,departments.py,admin_users.py,auth.py} && touch knust_student_system/services/{__init__.py,face_recognition.py,students.py,recognition_logs.py,auth.py} && touch knust_student_system/tests/{__init__.py,test_students.py,test_auth.py,test_admin.py,test_colleges.py,test_departments.py}
```

## Step-by-Step Guide to Set Up the Project

### Step 1: Set Up the Environment

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install required dependencies by creating requirements.txt:

```
fastapi==0.115.2
uvicorn==0.32.0
pydantic==2.9.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
supabase==2.9.1
face_recognition==1.3.0
numpy==1.26.4
pytest==8.3.3
httpx==0.27.2
python-multipart==0.0.12
pyotp==2.9.0
aiosmtplib==3.0.2
```