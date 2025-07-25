# KNUST Student Management System

A FastAPI-based student management system with facial recognition capabilities for KNUST (Kwame Nkrumah University of Science and Technology).

## Features

- 👤 Student Management
  - Registration with facial recognition
  - Student information management
  - Face recognition-based verification
  
- 🏛 Academic Structure Management
  - College management
  - Department management
  - Hierarchical organization structure
  
- 🔐 Security & Authentication
  - Admin authentication with JWT
  - Email-based OTP verification
  - Role-based access control
  
- 🎯 Face Recognition
  - Face detection and encoding
  - Real-time face recognition
  - Recognition logging
  
- 📊 Admin Dashboard
  - Student statistics
  - Recognition logs
  - System monitoring

## Technology Stack

- **Backend**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Face Recognition**: face_recognition
- **Authentication**: JWT, OTP
- **Email**: SMTP with SSL/TLS support
- **Testing**: pytest, httpx

## Prerequisites

- Python 3.10+
- pip
- PostgreSQL (via Supabase)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd knust_student_system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (.env):
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SECRET_KEY=your_secret_key
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email
EMAIL_PASSWORD=your_app_password
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Testing

The project includes two testing utilities:

1. Python-based testing (`test_api.py`):
```bash
python test_api.py
```

2. Shell-based testing (`test_requests.sh`):
```bash
chmod +x test_requests.sh
./test_requests.sh
```

## API Endpoints

### Authentication
- POST `/auth/register` - Register new admin
- POST `/auth/verify-otp` - Verify OTP
- POST `/auth/token` - Get access token

### Students
- POST `/students/` - Register new student
- GET `/students/` - List all students
- GET `/students/{id}` - Get student details
- PUT `/students/{id}` - Update student
- DELETE `/students/{id}` - Delete student
- POST `/students/recognize` - Recognize student

### Colleges
- POST `/colleges/` - Create college
- GET `/colleges/` - List colleges
- GET `/colleges/{id}` - Get college details
- PUT `/colleges/{id}` - Update college
- DELETE `/colleges/{id}` - Delete college

### Departments
- POST `/departments/` - Create department
- GET `/departments/` - List departments
- GET `/departments/{id}` - Get department details
- PUT `/departments/{id}` - Update department
- DELETE `/departments/{id}` - Delete department

### Admin Dashboard
- GET `/admin/stats` - Get system statistics
- GET `/admin/recognition-logs` - Get recognition logs

## Response Format

All API endpoints return responses in a standardized format:
```json
{
  "message": "Operation description",
  "status_code": 200,
  "count": 1,
  "data": [...]
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:
```json
{
  "message": "Error description",
  "status_code": 400,
  "count": 0,
  "data": null
}
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
