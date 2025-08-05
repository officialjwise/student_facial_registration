# 🏛️ KNUST Exam Room Management - Postman Testing Guide

## 📋 Overview

This guide provides comprehensive instructions for testing the KNUST Student System Exam Room Management API using the provided Postman collection. The collection includes all endpoints for exam room assignment, student validation, face recognition, and analytics.

## 📦 Collection Contents

- **Collection**: `KNUST_Exam_Room_Management.postman_collection.json`
- **Environment**: `KNUST_Exam_Room_Management.postman_environment.json`

## 🚀 Quick Setup

### 1. Import Collection and Environment

1. **Open Postman**
2. **Import Collection**:
   - Click "Import" → "Upload Files"
   - Select `KNUST_Exam_Room_Management.postman_collection.json`
3. **Import Environment**:
   - Click "Import" → "Upload Files"
   - Select `KNUST_Exam_Room_Management.postman_environment.json`
4. **Set Environment**:
   - Select "KNUST Exam Room Management Environment" from the environment dropdown

### 2. Configure Environment Variables

The following variables are pre-configured but can be customized:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `admin_email` | `admin@knust.edu.gh` | Admin login email |
| `admin_password` | `Admin123!` | Admin login password |
| `sample_student_index` | `20100025` | Test student index number |
| `test_room_code` | `ROOM_A1` | Test room code |

### 3. Start the API Server

Ensure your KNUST Student System API is running:

```bash
# From the project directory
source venv/bin/activate
uvicorn main:app --reload

# Or use VS Code task
# Run: "Run FastAPI server"
```

## 📊 Collection Structure

### 🔍 1. Health & Setup
- **Health Check**: Verify API is running
- **Admin Login**: Get JWT token for protected endpoints

### 🏛️ 2. Exam Room Management
- **Create Exam Room - Room A1**: Create first test room
- **Create Exam Room - Room B2**: Create second test room
- **Create Exam Room - Room C3**: Create third test room

### 📋 3. View & Manage Rooms
- **List All Room Mappings**: View all room assignments (public)
- **Get Specific Room by ID**: Get individual room details (protected)
- **Update Room Assignment**: Modify existing room (protected)

### 🎯 4. Student Validation & Recognition
- **Test Index Number Validation - Valid**: Test valid index number
- **Test Index Number Validation - Invalid**: Test invalid index number
- **Face Recognition - Valid Student**: Test face recognition with room validation
- **Face Recognition - No Face Image**: Test error handling
- **Face Recognition - Invalid Base64**: Test invalid image format

### 📊 5. Analytics & Monitoring
- **Registration Trends**: Get registration analytics
- **College Distribution**: Get college distribution data
- **Department Enrollment**: Get department enrollment stats
- **System Health**: Get system health metrics
- **Admin Dashboard**: Get comprehensive dashboard data

### 🧪 6. Error Handling & Edge Cases
- **Create Room with Duplicate Code**: Test duplicate prevention
- **Get Non-existent Room**: Test 404 handling
- **Access Protected Endpoint Without Auth**: Test authentication
- **Validate Non-existent Room**: Test validation edge cases

### 🧹 7. Cleanup (Optional)
- **Delete Room A1**: Remove test room A1
- **Delete Room B2**: Remove test room B2
- **Delete Room C3**: Remove test room C3
- **Verify Cleanup**: Confirm rooms were deleted

## 🎯 Testing Workflow

### Recommended Testing Order

1. **Start with Health Check** ✅
   - Verify API is accessible
   - Check response format

2. **Authenticate** 🔐
   - Run "Admin Login" request
   - JWT token will be automatically stored

3. **Create Test Data** 🏗️
   - Create Room A1, B2, and C3
   - Room IDs will be automatically stored

4. **Test Core Functionality** 🧪
   - List room mappings
   - Test student validation
   - Test face recognition

5. **Test Analytics** 📊
   - Check dashboard endpoints
   - Verify data structure

6. **Test Error Handling** ⚠️
   - Run error scenario tests
   - Verify proper error responses

7. **Cleanup (Optional)** 🧹
   - Delete test rooms
   - Verify cleanup completed

### Running All Tests

You can run the entire collection:

1. **Collection Runner**:
   - Click "Collections" → "KNUST Exam Room Management API"
   - Click "Run collection"
   - Select environment: "KNUST Exam Room Management Environment"
   - Click "Run KNUST Exam Room Management API"

2. **Monitor Results**:
   - All tests include assertions
   - Green = Passed, Red = Failed
   - Check console for detailed logs

## 📝 Key Test Scenarios

### 1. Room Assignment Testing

```json
// Create Room Request
{
    "room_code": "ROOM_A1",
    "room_name": "Main Hall A1",
    "index_start": "20100001",
    "index_end": "20100050",
    "capacity": 50,
    "description": "Main examination hall"
}
```

**Expected Response**: 201 Created with room data including UUID

### 2. Student Validation Testing

**Valid Student**: Index `20100025` in `ROOM_A1` (range: 20100001-20100050)
- Expected: `is_valid: true`

**Invalid Student**: Index `20100075` in `ROOM_A1` (outside range)
- Expected: `is_valid: false`

### 3. Face Recognition Testing

```json
// Recognition Request
{
    "face_image": "base64_encoded_image_data",
    "room_code": "ROOM_A1"
}
```

**Expected Response Structure**:
```json
{
    "status": "valid|invalid",
    "beep_type": "confirmation|warning",
    "student_name": "Student Name",
    "index_number": "20100025",
    "room_code": "ROOM_A1",
    "message": "Validation message",
    "timestamp": "2025-08-03T12:00:00Z"
}
```

## 🔍 Automated Test Assertions

The collection includes comprehensive test assertions:

### Global Tests (All Requests)
- Response time < 5000ms
- JSON content-type for successful responses

### Specific Endpoint Tests
- **Health Check**: Status 200, contains "KNUST"
- **Login**: Status 200, access token present
- **Create Room**: Status 201, room data returned
- **List Rooms**: Status 200, array of rooms
- **Validation**: Status 200, validation result structure
- **Analytics**: Status 200, expected data structure
- **Error Cases**: Proper error status codes and messages

## 🐛 Troubleshooting

### Common Issues

1. **Login Failed**
   - Check admin credentials in environment
   - Verify admin user exists in database
   - Check server logs for authentication errors

2. **Token Expired**
   - Re-run "Admin Login" request
   - Check token expiration settings

3. **Room Creation Failed**
   - Check for duplicate room codes
   - Verify index number format
   - Check database connectivity

4. **Face Recognition Errors**
   - Verify base64 image format
   - Check if student exists in database
   - Ensure face encodings are stored

### Debug Commands

```bash
# Check API status
curl http://localhost:8000/

# Test admin login manually
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@knust.edu.gh", "password": "Admin123!"}'

# Check room mappings
curl http://localhost:8000/exam-room/mappings
```

## 📊 Environment Variables Reference

### Automatic Variables (Set by Tests)
- `jwt_token`: JWT access token from login
- `room_a1_id`: UUID of created Room A1
- `room_b2_id`: UUID of created Room B2
- `room_c3_id`: UUID of created Room C3

### Manual Configuration
- `base_url`: Change for different environments
- `admin_email`: Update for different admin users
- `admin_password`: Update for different passwords
- `sample_base64_image`: Replace with actual face image data

## 🎨 Custom Testing

### Adding New Test Cases

1. **Duplicate Request**:
   - Right-click on existing request → "Duplicate"
   - Modify request data as needed
   - Update test assertions

2. **Add Test Script**:
   ```javascript
   pm.test("Your test description", function () {
       const responseJson = pm.response.json();
       pm.expect(responseJson.data).to.have.property('expected_field');
   });
   ```

3. **Set Environment Variables**:
   ```javascript
   pm.environment.set("variable_name", "value");
   ```

### Testing with Real Data

Replace sample data with actual:
- Upload real student face images (base64 encoded)
- Use actual student index numbers
- Create rooms with realistic capacity and descriptions

## 📈 Reporting

### Test Results
- Use Postman's built-in reporting
- Export results to Newman for CI/CD
- Generate HTML reports for stakeholders

### Performance Monitoring
- Check response times in test results
- Monitor API performance trends
- Set up alerts for slow responses

## 🔒 Security Considerations

1. **Sensitive Data**: Use environment variables for credentials
2. **Token Management**: Tokens automatically expire for security
3. **Test Data**: Clean up test data after testing
4. **Production**: Use separate environment for production testing

---

## 🎯 Success Criteria

After running the full collection, you should see:

✅ **Health Check**: API is accessible  
✅ **Authentication**: JWT token obtained  
✅ **Room Management**: CRUD operations working  
✅ **Validation**: Student-room validation functional  
✅ **Recognition**: Face recognition with room context  
✅ **Analytics**: Dashboard data available  
✅ **Error Handling**: Proper error responses  
✅ **Cleanup**: Test data removed  

## 📞 Support

For issues with the Postman collection:

1. Check server logs for detailed error messages
2. Verify environment variable values
3. Ensure database migration has been run
4. Test individual endpoints manually if needed

**Happy Testing!** 🚀
