# KNUST Student System API - Updated Authentication & Authorization

## 🔄 Recent Changes

### 1. Public Student Registration
- **Changed**: `POST /students/` is now a **public endpoint**
- **Reason**: Allow students to self-register without admin authentication
- **New**: Added `POST /students/admin/create` for admin-only student creation

### 2. Enhanced Authentication Flow
- **New OTP-based Login**: Two-step authentication process for admins
- **Refresh Tokens**: Added support for token refresh mechanism
- **Backward Compatibility**: Legacy direct login still available

## 📋 Updated Endpoints Summary

### 🔓 Public Endpoints (No Authentication Required)
- `GET /` - Health check
- `POST /auth/register` - Admin registration
- `POST /auth/verify-otp` - OTP verification for registration
- `POST /auth/login-otp` - Request OTP for login
- `POST /auth/verify-login-otp` - Verify login OTP and get tokens
- `GET /colleges/` - List all colleges
- `GET /departments/` - List all departments (with optional college filter)
- `POST /students/` - **Student self-registration** 🆕
- `POST /students/recognize` - Face recognition

### 🔒 Protected Endpoints (Require JWT Token)

#### Admin Management
- `GET /admin/stats` - Dashboard statistics
- `GET /admin/students` - All students (admin view)
- `GET /admin/recognition-logs` - Recognition logs with filters
- `PUT /admin/{admin_id}` - Update admin details
- `DELETE /admin/{admin_id}` - Delete admin

#### College Management
- `POST /colleges/` - Create college
- `GET /colleges/{college_id}` - Get college by ID
- `PUT /colleges/{college_id}` - Update college
- `DELETE /colleges/{college_id}` - Delete college

#### Department Management
- `POST /departments/` - Create department
- `GET /departments/{department_id}` - Get department by ID
- `PUT /departments/{department_id}` - Update department
- `DELETE /departments/{department_id}` - Delete department

#### Student Management (Admin Only)
- `POST /students/admin/create` - **Admin-only student creation** 🆕
- `GET /students/` - List all students
- `GET /students/{student_id}` - Get student by ID
- `PUT /students/{student_id}` - Update student
- `DELETE /students/{student_id}` - Delete student

#### Token Management
- `POST /auth/login` - Legacy direct login (still available)
- `POST /auth/refresh` - Refresh access token

## 🔐 Authentication Flows

### Option 1: OTP-Based Login (Recommended)
1. **Request OTP**: `POST /auth/login-otp`
   ```json
   {
     "email": "admin@knust.edu.gh",
     "password": "your_password"
   }
   ```

2. **Verify OTP**: `POST /auth/verify-login-otp`
   ```json
   {
     "email": "admin@knust.edu.gh",
     "otp": "123456"
   }
   ```

3. **Response**: Access & Refresh tokens
   ```json
   {
     "access_token": "...",
     "refresh_token": "...",
     "token_type": "bearer"
   }
   ```

### Option 2: Legacy Direct Login
1. **Direct Login**: `POST /auth/login`
   ```
   Form data:
   username: admin@knust.edu.gh
   password: your_password
   ```

2. **Response**: Access & Refresh tokens
   ```json
   {
     "access_token": "...",
     "refresh_token": "...",
     "token_type": "bearer"
   }
   ```

### Token Refresh
When access token expires, use refresh token:
```json
POST /auth/refresh
{
  "refresh_token": "your_refresh_token"
}
```

## 🎯 Key Changes for Frontend Integration

### 1. Student Registration
- **Public Access**: No authentication needed for student self-registration
- **Admin Alternative**: Use `/students/admin/create` for admin-managed registration

### 2. Authentication Headers
- **Format**: `Authorization: Bearer <access_token>`
- **Token Lifespan**: Access tokens expire in 30 minutes (configurable)
- **Refresh**: Refresh tokens expire in 7 days

### 3. Response Format
All endpoints return standardized responses:
```json
{
  "message": "Operation description",
  "status_code": 200,
  "count": 1,
  "data": [/* response data */]
}
```

## 📦 Postman Testing

Import the provided files for comprehensive API testing:
1. `KNUST_Student_System_API_Tests.postman_collection.json` - Complete test suite
2. `KNUST_Student_System.postman_environment.json` - Environment variables

### Test Sequence:
1. **Authentication Flow**: Register → Verify OTP → Login OTP → Verify Login OTP
2. **Setup Data**: Create College → Create Department
3. **Student Management**: Public Registration → Admin Creation → CRUD operations
4. **Face Recognition**: Upload image for recognition
5. **Admin Dashboard**: Stats → Logs → Management

## 🔧 Environment Variables (Postman)
- `base_url`: API base URL (default: http://localhost:8000)
- `access_token`: JWT access token (auto-set from login responses)
- `refresh_token`: JWT refresh token (auto-set from login responses)
- `college_id`: Created college ID (auto-set from college creation)
- `department_id`: Created department ID (auto-set from department creation)
- `student_id`: Created student ID (auto-set from student creation)

## 🚀 Getting Started

1. **Start the API**:
   ```bash
   # From project root
   source venv/bin/activate  # or your virtual environment
   uvicorn main:app --reload
   ```

2. **Import Postman Collection**:
   - Import `KNUST_Student_System_API_Tests.postman_collection.json`
   - Import `KNUST_Student_System.postman_environment.json`
   - Set the environment to "KNUST Student System Environment"

3. **Run Tests**:
   - Execute requests in sequence
   - Check that tokens are automatically saved to environment variables
   - Verify public endpoints work without authentication
   - Confirm protected endpoints require valid tokens

## 🔍 Error Handling

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request
- `401`: Unauthorized (invalid/expired token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `409`: Conflict (duplicate data)
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

### OTP-Related Errors
- Invalid OTP format (must be 6 digits)
- Expired OTP (5-minute window)
- Invalid email/password combination
- Account not verified

This comprehensive update provides better security with OTP verification while maintaining public access for student registration and recognition features.
