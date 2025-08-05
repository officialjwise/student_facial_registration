#!/bin/bash

# KNUST Exam Room Management - Quick API Test
# This script provides a quick test of the exam room endpoints

echo "🏛️ KNUST Exam Room Management - Quick API Test"
echo "=============================================="

# Configuration
BASE_URL="http://localhost:8000"
ADMIN_EMAIL="admin@knust.edu.gh"
ADMIN_PASSWORD="Admin123!"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "SUCCESS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "ERROR" ]; then
        echo -e "${RED}❌ $message${NC}"
    elif [ "$status" = "INFO" ]; then
        echo -e "${BLUE}ℹ️  $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    fi
}

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local auth_header=$4
    local data=$5
    local description=$6
    
    print_status "INFO" "Testing: $description"
    
    if [ -n "$auth_header" ] && [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -H "$auth_header" \
            -d "$data" \
            "$BASE_URL$endpoint")
    elif [ -n "$auth_header" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "$auth_header" \
            "$BASE_URL$endpoint")
    elif [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            "$BASE_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq "$expected_status" ]; then
        print_status "SUCCESS" "$method $endpoint → $http_code"
    else
        print_status "ERROR" "$method $endpoint → Expected: $expected_status, Got: $http_code"
        echo "Response: $response_body"
    fi
    
    echo ""
    return $http_code
}

# Start testing
print_status "INFO" "Starting exam room management API tests..."
echo ""

# Test 1: Health Check
test_endpoint "GET" "/" 200 "" "" "Health Check"

# Test 2: Admin Login
login_data='{
    "email": "'$ADMIN_EMAIL'",
    "password": "'$ADMIN_PASSWORD'"
}'

print_status "INFO" "Attempting admin login..."
response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d "$login_data" \
    "$BASE_URL/auth/login")

http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | head -n -1)

if [ "$http_code" -eq 200 ]; then
    print_status "SUCCESS" "Admin login successful"
    # Extract token (basic parsing)
    access_token=$(echo "$response_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$access_token" ]; then
        auth_header="Authorization: Bearer $access_token"
        print_status "SUCCESS" "JWT token extracted"
    else
        print_status "ERROR" "Failed to extract JWT token"
        echo "Response: $response_body"
        exit 1
    fi
else
    print_status "ERROR" "Admin login failed - $http_code"
    echo "Response: $response_body"
    exit 1
fi
echo ""

# Test 3: List Room Mappings (Public)
test_endpoint "GET" "/exam-room/mappings" 200 "" "" "List Room Mappings (Public)"

# Test 4: Create Exam Room
room_data='{
    "room_code": "TEST_ROOM_001",
    "room_name": "Test Room 001",
    "index_start": "20999001",
    "index_end": "20999050",
    "capacity": 50,
    "description": "Test room created by API test script"
}'

test_endpoint "POST" "/exam-room/assign" 201 "$auth_header" "$room_data" "Create Test Room"

# Test 5: Validate Student (Valid Range)
test_endpoint "GET" "/exam-room/validate/TEST_ROOM_001/20999025" 200 "" "" "Validate Student in Range"

# Test 6: Validate Student (Invalid Range)
test_endpoint "GET" "/exam-room/validate/TEST_ROOM_001/20999099" 200 "" "" "Validate Student Out of Range"

# Test 7: Face Recognition (Will fail without valid image, but tests endpoint)
recognition_data='{
    "face_image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "room_code": "TEST_ROOM_001"
}'

test_endpoint "POST" "/exam-room/recognize" 200 "" "$recognition_data" "Face Recognition Test"

# Test 8: Analytics Endpoints (Protected)
test_endpoint "GET" "/admin/analytics/registration-trends" 200 "$auth_header" "" "Registration Trends Analytics"
test_endpoint "GET" "/admin/analytics/college-distribution" 200 "$auth_header" "" "College Distribution Analytics"
test_endpoint "GET" "/admin/analytics/system-health" 200 "$auth_header" "" "System Health Analytics"
test_endpoint "GET" "/admin/dashboard" 200 "$auth_header" "" "Admin Dashboard"

# Test 9: Error Handling Tests
print_status "INFO" "Testing error handling..."

# Unauthorized access
test_endpoint "POST" "/exam-room/assign" 401 "" "$room_data" "Unauthorized Access Test"

# Invalid data
invalid_data='{"invalid": "data"}'
test_endpoint "POST" "/exam-room/assign" 422 "$auth_header" "$invalid_data" "Invalid Data Test"

# Non-existent room
test_endpoint "GET" "/exam-room/validate/NONEXISTENT_ROOM/20999025" 200 "" "" "Non-existent Room Test"

echo ""
print_status "INFO" "Testing completed!"
print_status "WARNING" "Note: Some tests may fail if database is not properly set up"
print_status "WARNING" "Face recognition tests require actual student data"
print_status "INFO" "For comprehensive testing, use the Postman collection"

echo ""
echo "📋 Next Steps:"
echo "1. Check server logs for any errors"
echo "2. Run database migration if tables don't exist"
echo "3. Use Postman collection for detailed testing"
echo "4. Add real student data for face recognition testing"
echo ""
print_status "SUCCESS" "Quick API test completed! 🚀"
