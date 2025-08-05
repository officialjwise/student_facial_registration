# 👑 Admin Panel API Endpoints Guide

## 🔐 **Authentication Required**
All admin endpoints require Bearer token authentication:
```javascript
headers: {
  'Authorization': `Bearer ${access_token}`,
  'Content-Type': 'application/json'
}
```

---

## 🏠 **Dashboard & Statistics**

### **GET `/admin/stats`** - Dashboard Overview
```javascript
const getDashboardStats = async () => {
  const response = await fetch('/admin/stats', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const result = await response.json();
  
  // Returns:
  // {
  //   "data": [{
  //     "total_students": 150,
  //     "total_recognitions": 1250,
  //     "recent_recognitions": 45
  //   }]
  // }
};
```

---

## 👤 **Authentication Management**

### **POST `/auth/register`** - Register New Admin
```javascript
const registerAdmin = async (adminData) => {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: "admin@knust.edu.gh",
      password: "secure_password",
      full_name: "John Doe",
      role: "admin"
    })
  });
};
```

### **POST `/auth/verify-otp`** - Verify Admin Registration
```javascript
const verifyAdminOTP = async (email, otp) => {
  const response = await fetch('/auth/verify-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, otp })
  });
};
```

### **POST `/auth/login-otp`** - Request Login OTP
```javascript
const requestLoginOTP = async (email, password) => {
  const response = await fetch('/auth/login-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
};
```

### **POST `/auth/verify-login-otp`** - Verify Login & Get Tokens
```javascript
const verifyLoginOTP = async (email, otp) => {
  const response = await fetch('/auth/verify-login-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, otp })
  });
  
  const result = await response.json();
  // Returns: { access_token, refresh_token, token_type }
};
```

### **POST `/auth/refresh`** - Refresh Access Token
```javascript
const refreshToken = async (refresh_token) => {
  const response = await fetch('/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token })
  });
};
```

---

## 🎓 **Student Management**

### **GET `/admin/students`** - List All Students
```javascript
const getAllStudents = async () => {
  const response = await fetch('/admin/students', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const result = await response.json();
  // Returns array of all students
};
```

### **POST `/students/admin`** - Create Student (Admin)
```javascript
const createStudent = async (studentData) => {
  const response = await fetch('/students/admin', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      student_id: "12345678",
      first_name: "John",
      last_name: "Doe",
      email: "john.doe@student.knust.edu.gh",
      index_number: "1234567890",
      phone_number: "+233501234567",
      date_of_birth: "2000-01-15",
      gender: "Male",
      program: "BSc Computer Science",
      level: "300",
      college_id: "uuid-here",
      department_id: "uuid-here",
      face_image: "base64-image-data" // Optional
    })
  });
};
```

### **GET `/students/{student_id}`** - Get Student Details
```javascript
const getStudentById = async (studentId) => {
  const response = await fetch(`/students/${studentId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

### **GET `/students`** - List Students (Admin View)
```javascript
const getStudents = async () => {
  const response = await fetch('/students', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

### **PUT `/students/{student_id}`** - Update Student
```javascript
const updateStudent = async (studentId, updateData) => {
  const response = await fetch(`/students/${studentId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updateData)
  });
};
```

### **DELETE `/students/{student_id}`** - Delete Student
```javascript
const deleteStudent = async (studentId) => {
  const response = await fetch(`/students/${studentId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

---

## 📊 **Recognition Logs & Analytics**

### **GET `/admin/recognition-logs`** - Get Recognition Logs
```javascript
const getRecognitionLogs = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.student_id) params.append('student_id', filters.student_id);
  if (filters.start_date) params.append('start_date', filters.start_date);
  if (filters.end_date) params.append('end_date', filters.end_date);
  
  const response = await fetch(`/admin/recognition-logs?${params}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  // Returns array of recognition logs with timestamps
};
```

---

## 🏫 **College Management**

### **POST `/colleges/`** - Create College
```javascript
const createCollege = async (collegeData) => {
  const response = await fetch('/colleges/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: "College of Engineering",
      code: "COE",
      description: "College of Engineering"
    })
  });
};
```

### **GET `/colleges/`** - List All Colleges (Public)
```javascript
const getColleges = async () => {
  const response = await fetch('/colleges/');
  // No auth required - public endpoint
};
```

### **GET `/colleges/{college_id}`** - Get College Details
```javascript
const getCollegeById = async (collegeId) => {
  const response = await fetch(`/colleges/${collegeId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

### **PUT `/colleges/{college_id}`** - Update College
```javascript
const updateCollege = async (collegeId, updateData) => {
  const response = await fetch(`/colleges/${collegeId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updateData)
  });
};
```

### **DELETE `/colleges/{college_id}`** - Delete College
```javascript
const deleteCollege = async (collegeId) => {
  const response = await fetch(`/colleges/${collegeId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

---

## 🏛️ **Department Management**

### **POST `/departments/`** - Create Department
```javascript
const createDepartment = async (departmentData) => {
  const response = await fetch('/departments/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: "Computer Science & Informatics",
      code: "CSI",
      college_id: "college-uuid-here",
      description: "Department of Computer Science"
    })
  });
};
```

### **GET `/departments/`** - List Departments
```javascript
const getDepartments = async (collegeId = null) => {
  const url = collegeId 
    ? `/departments/?college_id=${collegeId}`
    : '/departments/';
  
  const response = await fetch(url);
  // No auth required - public endpoint
};
```

### **GET `/departments/{department_id}`** - Get Department Details
```javascript
const getDepartmentById = async (departmentId) => {
  const response = await fetch(`/departments/${departmentId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

### **PUT `/departments/{department_id}`** - Update Department
```javascript
const updateDepartment = async (departmentId, updateData) => {
  const response = await fetch(`/departments/${departmentId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updateData)
  });
};
```

### **DELETE `/departments/{department_id}`** - Delete Department
```javascript
const deleteDepartment = async (departmentId) => {
  const response = await fetch(`/departments/${departmentId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

---

## 👥 **Admin User Management**

### **PUT `/admin/{admin_id}`** - Update Admin Details
```javascript
const updateAdminUser = async (adminId, updateData) => {
  const response = await fetch(`/admin/${adminId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      full_name: "Updated Name",
      email: "new.email@knust.edu.gh",
      role: "admin"
    })
  });
};
```

### **DELETE `/admin/{admin_id}`** - Delete Admin User
```javascript
const deleteAdminUser = async (adminId) => {
  const response = await fetch(`/admin/${adminId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

---

## 🎯 **Face Recognition Features**

### **POST `/students/detect-face`** - Face Detection Preview
```javascript
const detectFace = async (imageData) => {
  const response = await fetch('/students/detect-face', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ face_image: imageData })
  });
  
  // Returns bounding box coordinates for face overlay
};
```

### **POST `/students/recognize`** - Recognize Student
```javascript
const recognizeStudent = async (imageData) => {
  const response = await fetch('/students/recognize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ face_image: imageData })
  });
  
  // Returns matched student info and confidence score
};
```

---

## 📋 **Admin Panel Feature Checklist**

### **Essential Features:**
- ✅ Dashboard with stats (`/admin/stats`)
- ✅ Student CRUD operations
- ✅ Recognition logs and analytics
- ✅ College management
- ✅ Department management
- ✅ Admin user management
- ✅ Face detection & recognition tools

### **Advanced Features:**
- 📊 Analytics and reporting
- 🔍 Advanced search and filtering
- 📤 Data export functionality
- 🔔 Real-time notifications
- 👥 Bulk operations
- 🎯 Face recognition testing tools

### **Security Features:**
- 🔐 JWT token authentication
- 📧 OTP-based login
- 🔄 Token refresh mechanism
- 🛡️ Role-based access control

---

## 🎨 **Example React Component Structure**

```jsx
// Admin Dashboard Structure
const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [students, setStudents] = useState([]);
  const [colleges, setColleges] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [recognitionLogs, setRecognitionLogs] = useState([]);

  // Component sections:
  // - DashboardStats (/admin/stats)
  // - StudentManagement (/admin/students, /students/*)
  // - CollegeManagement (/colleges/*)
  // - DepartmentManagement (/departments/*)
  // - RecognitionLogs (/admin/recognition-logs)
  // - AdminSettings (/admin/*)
};
```

This comprehensive endpoint list covers all administrative functions needed for a complete admin panel! 🚀
