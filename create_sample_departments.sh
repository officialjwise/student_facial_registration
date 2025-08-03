#!/bin/bash

# Quick script to create sample colleges and departments
# Make sure your FastAPI server is running and you have admin access

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

# You need to replace this with your actual admin token
# Get token from: POST /auth/login-otp -> POST /auth/verify-login-otp
TOKEN="YOUR-ADMIN-TOKEN-HERE"
AUTH_HEADER="Authorization: Bearer $TOKEN"

if [ "$TOKEN" = "YOUR-ADMIN-TOKEN-HERE" ]; then
    echo "❌ Please update the TOKEN variable with your actual admin token"
    echo "Get your token by:"
    echo "1. POST /auth/login-otp"  
    echo "2. POST /auth/verify-login-otp"
    echo "3. Copy the access_token from response"
    exit 1
fi

echo "🏛️ Creating Sample Colleges and Departments"
echo "=========================================="

# Create colleges first
echo "📚 Creating Colleges..."

ENGINEERING_COLLEGE=$(curl -s -X POST "$BASE_URL/colleges/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{"name": "College of Engineering"}')

SCIENCE_COLLEGE=$(curl -s -X POST "$BASE_URL/colleges/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{"name": "College of Science"}')

BUSINESS_COLLEGE=$(curl -s -X POST "$BASE_URL/colleges/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d '{"name": "College of Business Administration"}')

# Extract college IDs
ENG_ID=$(echo $ENGINEERING_COLLEGE | jq -r '.data[0].id')
SCI_ID=$(echo $SCIENCE_COLLEGE | jq -r '.data[0].id')
BUS_ID=$(echo $BUSINESS_COLLEGE | jq -r '.data[0].id')

echo "✅ Engineering College ID: $ENG_ID"
echo "✅ Science College ID: $SCI_ID" 
echo "✅ Business College ID: $BUS_ID"

if [ "$ENG_ID" = "null" ]; then
    echo "❌ Failed to create colleges. Check your token and permissions."
    exit 1
fi

echo ""
echo "🏢 Creating Departments..."

# Engineering Departments
echo "Creating Computer Science..."
curl -s -X POST "$BASE_URL/departments/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"name\": \"Computer Science\",
    \"college_id\": \"$ENG_ID\",
    \"department_head\": \"Dr. John Smith\",
    \"description\": \"The Computer Science Department focuses on software engineering, artificial intelligence, data science, and computational theory. We offer comprehensive programs for technology careers.\"
  }" | jq .

echo "Creating Electrical Engineering..."
curl -s -X POST "$BASE_URL/departments/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"name\": \"Electrical Engineering\",
    \"college_id\": \"$ENG_ID\",
    \"department_head\": \"Prof. Sarah Johnson\",
    \"description\": \"Specializes in power systems, electronics, telecommunications, and control systems. Programs combine theory with practical applications.\"
  }" | jq .

echo "Creating Mechanical Engineering..."
curl -s -X POST "$BASE_URL/departments/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"name\": \"Mechanical Engineering\",
    \"college_id\": \"$ENG_ID\",
    \"department_head\": \"Dr. Michael Brown\",
    \"description\": \"Covers thermodynamics, fluid mechanics, materials science, manufacturing, and robotics for automotive and aerospace industries.\"
  }" | jq .

# Science Departments  
echo "Creating Mathematics..."
curl -s -X POST "$BASE_URL/departments/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"name\": \"Mathematics\",
    \"college_id\": \"$SCI_ID\",
    \"department_head\": \"Dr. Emily Davis\",
    \"description\": \"Offers pure and applied mathematics, statistics, and computational mathematics. Develops analytical thinking and problem-solving skills.\"
  }" | jq .

echo "Creating Physics..."
curl -s -X POST "$BASE_URL/departments/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"name\": \"Physics\",
    \"college_id\": \"$SCI_ID\",
    \"department_head\": \"Prof. Robert Wilson\",
    \"description\": \"Explores fundamental principles of matter and energy. Programs in theoretical, experimental, and applied physics with quantum mechanics research.\"
  }" | jq .

# Business Departments
echo "Creating Business Administration..."
curl -s -X POST "$BASE_URL/departments/" \
  -H "$AUTH_HEADER" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"name\": \"Business Administration\",
    \"college_id\": \"$BUS_ID\",
    \"department_head\": \"Dr. James Taylor\",
    \"description\": \"Comprehensive programs in management, marketing, finance, and entrepreneurship. Prepares students for leadership roles.\"
  }" | jq .

echo ""
echo "📋 Fetching all departments to verify..."
curl -s "$BASE_URL/departments/" | jq .

echo ""
echo "✅ Sample departments created successfully!"
echo "🎯 Your frontend table should now show:"
echo "   - Department Name"
echo "   - College" 
echo "   - Department Head"
echo "   - Description"
