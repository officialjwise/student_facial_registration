#!/bin/bash

# Function to base64 encode an image
encode_image() {
    base64 -i "$1"
}

# 1. Register a student with a base64 encoded image
# Replace path/to/your/image.jpg with your actual image path
echo "Testing student registration with base64 image..."
curl -X POST "http://localhost:8000/students/" \
    -H "Content-Type: application/json" \
    -d "{
        \"student_id\": \"12345678\",
        \"index_number\": \"1234567\",
        \"first_name\": \"John\",
        \"last_name\": \"Doe\",
        \"email\": \"john.doe@example.com\",
        \"college_id\": \"YOUR-COLLEGE-UUID\",
        \"department_id\": \"YOUR-DEPARTMENT-UUID\",
        \"face_image\": \"$(encode_image path/to/your/image.jpg)\"
    }"

# 2. Test face recognition with file upload
echo "Testing face recognition with file upload..."
curl -X POST "http://localhost:8000/students/recognize" \
    -H "Content-Type: multipart/form-data" \
    -F "image=@path/to/your/image.jpg"
