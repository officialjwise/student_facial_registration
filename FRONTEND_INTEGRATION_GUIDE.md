# KNUST Student Management System - Frontend Integration Guide

## Project Overview

The KNUST Student Management System is a FastAPI-based backend that provides comprehensive student management with facial recognition capabilities. This document outlines all available API endpoints and their usage patterns for frontend integration.

**Base URL**: `http://localhost:8000` (Development)
**API Documentation**: `http://localhost:8000/docs` (Swagger UI)

## Authentication

The system uses JWT-based authentication for admin access. All admin-protected endpoints require a Bearer token in the Authorization header.

### Authentication Flow:
1. Admin registers → Receives OTP via email
2. Admin verifies OTP → Account activated
3. Admin logs in → Receives JWT token
4. Use token for subsequent API calls

**Header Format**: `Authorization: Bearer <jwt_token>`

---

## API Endpoints Reference

### 🔐 Authentication Endpoints

#### 1. Register Admin
```http
POST /auth/register
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "secure_password"
}
```

**Response (201)**:
```json
{
  "message": "Admin registered successfully. Please check your email for OTP verification.",
  "status_code": 201
}
```

**Validation**:
- Password must be at least 8 characters
- Valid email format required

#### 2. Verify OTP
```http
POST /auth/verify-otp
Content-Type: application/json

{
  "email": "admin@example.com",
  "otp": "123456"
}
```

**Response (200)**:
```json
{
  "message": "Account verified successfully"
}
```

**Validation**:
- OTP must be exactly 6 digits

#### 3. Login Admin
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@example.com&password=secure_password
```

**Response (200)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 👥 Student Management Endpoints

#### 1. Register Student with Facial Recognition
```http
POST /students/
Authorization: Bearer <token>
Content-Type: application/json

{
  "student_id": "12345678",
  "index_number": "1234567",
  "first_name": "John",
  "middle_name": "Paul",
  "last_name": "Doe",
  "email": "john.doe@student.knust.edu.gh",
  "college_id": "uuid-college-id",
  "department_id": "uuid-department-id",
  "face_image": "base64_encoded_image_string"
}
```

**Response (201)**:
```json
{
  "message": "Student registered successfully",
  "status_code": 201,
  "count": 1,
  "data": [{
    "id": "uuid",
    "student_id": "12345678",
    "index_number": "1234567",
    "first_name": "John",
    "middle_name": "Paul",
    "last_name": "Doe",
    "email": "john.doe@student.knust.edu.gh",
    "college_id": "uuid-college-id",
    "department_id": "uuid-department-id",
    "face_embedding": [0.123, 0.456, ...],
    "created_at": "2025-07-25T10:00:00Z"
  }]
}
```

**Validation Rules**:
- `student_id`: Exactly 8 digits
- `index_number`: Exactly 7 digits
- `face_image`: Base64-encoded JPEG/PNG, minimum 50x50 pixels, maximum 10MB
- Supports data URL format: `data:image/jpeg;base64,<base64_string>`

**Error Responses**:
- `409`: Duplicate student ID, index number, or email
- `400`: No face detected or invalid image
- `422`: Invalid data format

#### 2. Face Recognition (Client-Side)
```http
POST /students/recognize
Content-Type: multipart/form-data

image: <file_upload>
```

**Response (200)** - Student Found:
```json
{
  "message": "Student recognized successfully",
  "status_code": 200,
  "count": 1,
  "data": [{
    "id": "uuid",
    "student_id": "12345678",
    "first_name": "John",
    "last_name": "Doe",
    // ... full student details
  }]
}
```

**Response (404)** - No Match:
```json
{
  "detail": "No matching student found. Please try again with a clearer photo"
}
```

**File Requirements**:
- Format: JPEG, PNG
- Size: Maximum 10MB
- Quality: Clear face image, minimum 50x50 pixels
- Single face only

#### 3. Get All Students (Admin)
```http
GET /students/
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
  "message": "Students retrieved successfully",
  "status_code": 200,
  "count": 150,
  "data": [
    {
      "id": "uuid",
      "student_id": "12345678",
      // ... student details
    }
  ]
}
```

#### 4. Get Single Student (Admin)
```http
GET /students/{student_id}
Authorization: Bearer <token>
```

#### 5. Update Student (Admin)
```http
PUT /students/{student_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Updated Name",
  // ... other optional fields
}
```

#### 6. Delete Student (Admin)
```http
DELETE /students/{student_id}
Authorization: Bearer <token>
```

---

### 🏛️ College Management Endpoints

#### 1. Create College (Admin)
```http
POST /colleges/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "College of Engineering"
}
```

#### 2. Get All Colleges (Public)
```http
GET /colleges/
```

**Response (200)**:
```json
{
  "message": "Colleges retrieved successfully",
  "status_code": 200,
  "count": 6,
  "data": [
    {
      "id": "uuid",
      "name": "College of Engineering",
      "created_at": "2025-07-25T10:00:00Z"
    }
  ]
}
```

#### 3. Get Single College (Admin)
```http
GET /colleges/{college_id}
Authorization: Bearer <token>
```

#### 4. Update College (Admin)
```http
PUT /colleges/{college_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated College Name"
}
```

#### 5. Delete College (Admin)
```http
DELETE /colleges/{college_id}
Authorization: Bearer <token>
```

---

### 🏢 Department Management Endpoints

#### 1. Create Department (Admin)
```http
POST /departments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Computer Science",
  "college_id": "uuid-college-id"
}
```

#### 2. Get All Departments (Public)
```http
GET /departments/
```

#### 3. Get Departments by College (Public)
```http
GET /departments/?college_id=uuid-college-id
```

**Response (200)**:
```json
{
  "message": "Departments for college {college_id} retrieved successfully",
  "status_code": 200,
  "count": 12,
  "data": [
    {
      "id": "uuid",
      "name": "Computer Science",
      "college_id": "uuid-college-id",
      "created_at": "2025-07-25T10:00:00Z"
    }
  ]
}
```

#### 4. Get Single Department (Admin)
```http
GET /departments/{department_id}
Authorization: Bearer <token>
```

#### 5. Update Department (Admin)
```http
PUT /departments/{department_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Department Name",
  "college_id": "new-college-id"
}
```

#### 6. Delete Department (Admin)
```http
DELETE /departments/{department_id}
Authorization: Bearer <token>
```

---

### 📊 Admin Dashboard Endpoints

#### 1. Get Dashboard Statistics
```http
GET /admin/stats
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
  "message": "Admin statistics retrieved successfully",
  "status_code": 200,
  "count": 1,
  "data": [{
    "total_students": 1500,
    "total_recognitions": 2300,
    "recent_recognitions": 45
  }]
}
```

#### 2. Get All Students (Admin View)
```http
GET /admin/students
Authorization: Bearer <token>
```

#### 3. Get Recognition Logs
```http
GET /admin/recognition-logs
Authorization: Bearer <token>
```

**Optional Query Parameters**:
- `student_id`: Filter by specific student
- `start_date`: Filter from date (ISO format)
- `end_date`: Filter to date (ISO format)

**Response (200)**:
```json
{
  "message": "Recognition logs retrieved successfully",
  "status_code": 200,
  "count": 100,
  "data": [
    {
      "id": "uuid",
      "student_id": "uuid",
      "confidence_score": 0.95,
      "camera_source": "main_entrance",
      "timestamp": "2025-07-25T10:00:00Z"
    }
  ]
}
```

#### 4. Update Admin Details
```http
PUT /admin/{admin_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "new.email@example.com",
  "password": "new_password"
}
```

#### 5. Delete Admin User
```http
DELETE /admin/{admin_id}
Authorization: Bearer <token>
```

---

## Frontend Implementation Guidelines

### 1. Client-Side Face Recognition App

**Features to Implement**:
- Camera interface for capturing photos
- Real-time face detection preview
- Photo upload to `/students/recognize`
- Display recognition results
- Error handling for poor image quality

**Recommended Flow**:
```javascript
// Example React/JS implementation
const recognizeStudent = async (imageFile) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  try {
    const response = await fetch('/students/recognize', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (response.ok) {
      // Student found
      displayStudentInfo(result.data[0]);
    } else {
      // No match or error
      showError(result.detail);
    }
  } catch (error) {
    showError('Network error occurred');
  }
};
```

### 2. Admin Panel

**Required Pages**:

1. **Login/Registration Page**
   - Admin registration form
   - OTP verification form
   - Login form
   - JWT token storage

2. **Dashboard**
   - System statistics display (total students, recognitions, recent activity)
   - Recent activity logs
   - Quick navigation to other sections

3. **Student Management**
   - Student registration form with image upload
   - Student list with search/filter
   - Student detail view/edit
   - Bulk import functionality

4. **Academic Structure**
   - College management (CRUD)
   - Department management (CRUD)
   - Hierarchical display (College → Departments)

5. **Recognition Logs**
   - Recognition history table
   - Filtering by date/student
   - Export functionality

**Dashboard Statistics Implementation**:
```javascript
// Fetch dashboard stats
const fetchDashboardStats = async () => {
  try {
    const response = await fetch('/admin/stats', {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    });
    
    if (response.ok) {
      const result = await response.json();
      const stats = result.data[0];
      
      // Update UI with stats
      updateDashboard({
        totalStudents: stats.total_students,
        totalRecognitions: stats.total_recognitions,
        recentRecognitions: stats.recent_recognitions
      });
    } else if (response.status === 401) {
      // Token expired, redirect to login
      redirectToLogin();
    }
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error);
    showError('Failed to load dashboard statistics');
  }
};
```

**Image Handling Best Practices**:
```javascript
// Base64 encoding for student registration
const encodeImageToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

// Usage in registration form
const registerStudent = async (studentData, imageFile) => {
  const base64Image = await encodeImageToBase64(imageFile);
  
  const payload = {
    ...studentData,
    face_image: base64Image // Can include data URL prefix
  };
  
  const response = await fetch('/students/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwt_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
};
```

### 3. Error Handling

**Common Error Scenarios**:

```javascript
const handleAPIError = (response, result) => {
  switch (response.status) {
    case 401:
      // Redirect to login
      redirectToLogin();
      break;
    case 409:
      // Duplicate data
      showError('Student with this ID already exists');
      break;
    case 422:
      // Validation error
      showValidationErrors(result.detail);
      break;
    case 400:
      // Bad request (e.g., no face detected)
      showError(result.detail);
      break;
    case 500:
      // Server error
      showError('Server error. Please try again later.');
      break;
    default:
      showError('An unexpected error occurred');
  }
};
```

### 4. State Management

**Recommended State Structure**:
```javascript
// Global state structure
const appState = {
  auth: {
    isAuthenticated: false,
    token: null,
    user: null
  },
  students: {
    list: [],
    loading: false,
    error: null
  },
  colleges: {
    list: [],
    loading: false
  },
  departments: {
    list: [],
    loading: false
  },
  dashboard: {
    stats: null,
    logs: [],
    loading: false
  }
};
```

### 5. Performance Considerations

- **Image Optimization**: Compress images before upload
- **Pagination**: Implement for large student lists
- **Caching**: Cache colleges/departments data
- **Loading States**: Show loading indicators for all API calls
- **Offline Support**: Cache essential data for offline viewing

### 6. Security Considerations

- **Token Storage**: Use secure storage (httpOnly cookies or encrypted localStorage)
- **Token Refresh**: Implement token refresh mechanism
- **Input Validation**: Client-side validation matching server rules
- **Image Security**: Validate image types and sizes before upload
- **HTTPS**: Always use HTTPS in production

---

## Testing the API

**Sample Test Requests**:

```bash
# Test registration endpoint
curl -X POST "http://localhost:8000/students/recognize" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@test_photo.jpg"

# Test with invalid image
curl -X POST "http://localhost:8000/students/recognize" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@small_image.jpg"
```

---

## Recent Fixes and Troubleshooting

### Fixed Issues (July 25, 2025)

#### 1. Admin Dashboard Statistics Error ✅
**Issue**: The `/admin/stats` endpoint was returning 500 errors due to invalid SQL syntax in date filtering.

**Error Message**: 
```
ERROR: invalid input syntax for type timestamp with time zone: "now() - interval '7 days'"
```

**Fix Applied**: Updated the admin stats endpoint to calculate dates in Python instead of using PostgreSQL functions:
```javascript
// Before (causing error)
start_date="now() - interval '7 days'"

// After (working)
seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
start_date=seven_days_ago  // "2025-07-18T04:07:19.290970"
```

**Frontend Impact**: The dashboard statistics should now load correctly without errors.

#### 2. Image Validation Improvements ✅
**Issue**: Images were being rejected with overly restrictive size requirements (100x100px minimum).

**Fix Applied**: 
- Reduced minimum image size to 50x50 pixels (more reasonable for face recognition)
- Improved error messages for better user experience
- Added support for data URL prefixes in base64 images

**Frontend Impact**: More images will be accepted for face recognition, leading to better user experience.

#### 3. Face Recognition Error Handling ✅
**Issue**: 422 Unprocessable Entity errors were occurring due to improper validation.

**Fix Applied**:
- Better base64 validation with proper error handling
- Improved file upload validation
- More descriptive error messages

**Frontend Impact**: Users will receive clearer error messages when image uploads fail.

### Testing the Fixes

You can verify these fixes by:

1. **Testing Admin Stats**:
```javascript
fetch('/admin/stats', {
  headers: { 'Authorization': 'Bearer ' + token }
})
.then(response => response.json())
.then(data => console.log('Stats:', data))
.catch(error => console.error('Error:', error));
```

2. **Testing Face Recognition**:
```javascript
const formData = new FormData();
formData.append('image', imageFile);

fetch('/students/recognize', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log('Recognition result:', data));
```
