#!/bin/bash

# Test script for new analytics endpoints
# Make sure your FastAPI server is running first

BASE_URL="http://localhost:8000"
CONTENT_TYPE="Content-Type: application/json"

# You need to replace this with your actual admin token
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

echo "📊 Testing New Analytics Dashboard Endpoints"
echo "============================================="

echo ""
echo "1. 📈 Testing Comprehensive Dashboard Stats..."
curl -s -X GET "$BASE_URL/admin/stats" \
  -H "$AUTH_HEADER" | jq .

echo ""
echo "2. 📅 Testing Registration Trends (30 days)..."
curl -s -X GET "$BASE_URL/admin/analytics/registration-trends?days=30" \
  -H "$AUTH_HEADER" | jq .

echo ""
echo "3. 🥧 Testing College Distribution..."
curl -s -X GET "$BASE_URL/admin/analytics/college-distribution" \
  -H "$AUTH_HEADER" | jq .

echo ""
echo "4. 📊 Testing Department Enrollment (top 10)..."
curl -s -X GET "$BASE_URL/admin/analytics/department-enrollment?limit=10" \
  -H "$AUTH_HEADER" | jq .

echo ""
echo "5. 🏥 Testing System Health Metrics..."
curl -s -X GET "$BASE_URL/admin/analytics/system-health" \
  -H "$AUTH_HEADER" | jq .

echo ""
echo "6. 👥 Testing Admin Users Count..."
curl -s -X GET "$BASE_URL/admin/users/count" \
  -H "$AUTH_HEADER" | jq .

echo ""
echo "✅ Analytics Dashboard Endpoints Test Complete!"
echo ""
echo "📋 Summary of New Endpoints:"
echo "- GET /admin/stats (enhanced with all counts)"
echo "- GET /admin/analytics/registration-trends"
echo "- GET /admin/analytics/college-distribution"
echo "- GET /admin/analytics/department-enrollment"
echo "- GET /admin/analytics/system-health"
echo "- GET /admin/users/count"
echo ""
echo "📁 Import these Postman files:"
echo "- KNUST_Analytics_Dashboard.postman_collection.json"
echo "- KNUST_Analytics_Dashboard.postman_environment.json"
echo ""
echo "📖 Read ANALYTICS_POSTMAN_GUIDE.md for detailed usage instructions"
