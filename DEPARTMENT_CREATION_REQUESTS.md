# HTTP Request Bodies for Department Creation

## Prerequisites
Before creating departments, you need:
1. Admin authentication token
2. At least one college created (departments belong to colleges)

## Authentication
All creation requests require admin authentication:
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

## 1. Create Colleges First (Required)

### Create College of Engineering
```http
POST /colleges/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "College of Engineering"
}
```

### Create College of Science
```http
POST /colleges/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "College of Science"
}
```

### Create College of Business
```http
POST /colleges/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "College of Business Administration"
}
```

## 2. Create Departments (Use college IDs from above responses)

### Computer Science Department
```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Computer Science",
  "college_id": "REPLACE-WITH-ENGINEERING-COLLEGE-ID",
  "department_head": "Dr. John Smith",
  "description": "The Computer Science Department focuses on software engineering, artificial intelligence, data science, and computational theory. We offer comprehensive undergraduate and graduate programs designed to prepare students for careers in technology, research, and innovation."
}
```

### Electrical Engineering Department
```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Electrical Engineering", 
  "college_id": "REPLACE-WITH-ENGINEERING-COLLEGE-ID",
  "department_head": "Prof. Sarah Johnson",
  "description": "The Electrical Engineering Department specializes in power systems, electronics, telecommunications, control systems, and renewable energy. Our programs combine theoretical knowledge with hands-on practical applications."
}
```

### Mechanical Engineering Department
```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Mechanical Engineering",
  "college_id": "REPLACE-WITH-ENGINEERING-COLLEGE-ID", 
  "department_head": "Dr. Michael Brown",
  "description": "The Mechanical Engineering Department covers thermodynamics, fluid mechanics, materials science, manufacturing, and robotics. We prepare students for careers in automotive, aerospace, energy, and manufacturing industries."
}
```

### Mathematics Department
```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Mathematics",
  "college_id": "REPLACE-WITH-SCIENCE-COLLEGE-ID",
  "department_head": "Dr. Emily Davis",
  "description": "The Mathematics Department offers pure and applied mathematics, statistics, and computational mathematics. Our programs develop analytical thinking and problem-solving skills essential for scientific and technological advancement."
}
```

### Physics Department
```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Physics",
  "college_id": "REPLACE-WITH-SCIENCE-COLLEGE-ID",
  "department_head": "Prof. Robert Wilson",
  "description": "The Physics Department explores fundamental principles of matter, energy, and their interactions. We offer programs in theoretical physics, experimental physics, and applied physics with research opportunities in quantum mechanics and materials science."
}
```

### Chemistry Department
```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Chemistry",
  "college_id": "REPLACE-WITH-SCIENCE-COLLEGE-ID",
  "department_head": "Dr. Lisa Anderson",
  "description": "The Chemistry Department covers organic, inorganic, physical, and analytical chemistry. Our programs prepare students for careers in pharmaceuticals, materials science, environmental science, and chemical research."
}
```

### Business Administration Department
```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Business Administration",
  "college_id": "REPLACE-WITH-BUSINESS-COLLEGE-ID",
  "department_head": "Dr. James Taylor",
  "description": "The Business Administration Department offers comprehensive programs in management, marketing, finance, and entrepreneurship. We prepare students for leadership roles in various industries and business sectors."
}
```

### Accounting Department
```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Accounting",
  "college_id": "REPLACE-WITH-BUSINESS-COLLEGE-ID",
  "department_head": "Prof. Maria Garcia",
  "description": "The Accounting Department provides education in financial accounting, management accounting, auditing, and taxation. Our programs prepare students for careers as certified public accountants, financial analysts, and business consultants."
}
```

## 3. Minimal Department Creation (Optional Fields)

If you want to create departments without department head or description initially:

```http
POST /departments/
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "name": "Civil Engineering",
  "college_id": "REPLACE-WITH-ENGINEERING-COLLEGE-ID"
}
```

## 4. cURL Examples

### Create College with cURL
```bash
curl -X POST "http://localhost:8000/colleges/" \
  -H "Authorization: Bearer YOUR-TOKEN-HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "College of Engineering"
  }'
```

### Create Department with cURL
```bash
curl -X POST "http://localhost:8000/departments/" \
  -H "Authorization: Bearer YOUR-TOKEN-HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Computer Science",
    "college_id": "COLLEGE-UUID-HERE",
    "department_head": "Dr. John Smith",
    "description": "Computer Science Department description here"
  }'
```

## Notes:
1. Replace `REPLACE-WITH-*-COLLEGE-ID` with actual UUID from college creation responses
2. All fields except `name` and `college_id` are optional
3. `department_head` and `description` can be added later via PUT requests
4. Make sure to run the database migration first: `add_department_fields_migration.sql`
