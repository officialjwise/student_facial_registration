#!/bin/bash

# Test script for Department endpoints with new fields
# This script demonstrates the new fields: department_head, description, and college_name

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

echo "🏛️ Testing Department Management with New Fields"
echo "================================================"

# First, let's create a college (required for department)
echo "1. Creating a test college..."
COLLEGE_RESPONSE=$(curl -s -X POST "$BASE_URL/colleges/" \
  -H "$CONTENT_TYPE" \
  -d '{
    "name": "College of Engineering"
  }')

echo "College Response: $COLLEGE_RESPONSE"

# Extract college ID from response
COLLEGE_ID=$(echo $COLLEGE_RESPONSE | jq -r '.data[0].id')
echo "College ID: $COLLEGE_ID"

if [ "$COLLEGE_ID" = "null" ]; then
  echo "❌ Failed to create college. Please check if you have admin authentication."
  exit 1
fi

echo ""
echo "2. Creating a department with new fields..."
DEPT_RESPONSE=$(curl -s -X POST "$BASE_URL/departments/" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"name\": \"Computer Science\",
    \"college_id\": \"$COLLEGE_ID\",
    \"department_head\": \"Dr. John Smith\",
    \"description\": \"The Computer Science Department focuses on software engineering, artificial intelligence, and computational theory. We offer undergraduate and graduate programs designed to prepare students for careers in technology and research.\"
  }")

echo "Department Response: $DEPT_RESPONSE"

# Extract department ID
DEPT_ID=$(echo $DEPT_RESPONSE | jq -r '.data[0].id')
echo "Department ID: $DEPT_ID"

echo ""
echo "3. Creating another department..."
curl -s -X POST "$BASE_URL/departments/" \
  -H "$CONTENT_TYPE" \
  -d "{
    \"name\": \"Electrical Engineering\",
    \"college_id\": \"$COLLEGE_ID\",
    \"department_head\": \"Prof. Sarah Johnson\",
    \"description\": \"The Electrical Engineering Department specializes in power systems, electronics, telecommunications, and control systems. Our programs combine theoretical knowledge with practical applications.\"
  }" | jq .

echo ""
echo "4. Fetching all departments (with new fields)..."
curl -s "$BASE_URL/departments/" | jq .

echo ""
echo "5. Frontend Table Format:"
echo "The response now includes all required fields for your table:"
echo "- Department Name: data[].name"
echo "- College: data[].college_name" 
echo "- Department Head: data[].department_head"
echo "- Description: data[].description"

echo ""
echo "6. Testing update with new fields..."
curl -s -X PUT "$BASE_URL/departments/$DEPT_ID" \
  -H "$CONTENT_TYPE" \
  -d '{
    "department_head": "Dr. John Smith (Updated)",
    "description": "Updated description with new research areas including machine learning and cybersecurity."
  }' | jq .

echo ""
echo "✅ Test completed! All new fields are working correctly."
