# 📊 KNUST Analytics Dashboard - Postman Collection

## 🚀 Quick Start Guide

### 1. Import Collection & Environment
1. **Import Collection**: Import `KNUST_Analytics_Dashboard.postman_collection.json`
2. **Import Environment**: Import `KNUST_Analytics_Dashboard.postman_environment.json`
3. **Select Environment**: Choose "KNUST Analytics Dashboard Environment"

### 2. Set Up Authentication
Before using the analytics endpoints, you need an admin JWT token:

```bash
# Step 1: Register/Login Admin (if needed)
POST /auth/register
POST /auth/verify-otp

# Step 2: Get Admin Token
POST /auth/login-otp
POST /auth/verify-login-otp
```

**Copy the `access_token` from the response and set it in the environment variable `admin_token`.**

### 3. Update Base URL
- Set `base_url` to your server URL (default: `http://localhost:8000`)
- For production, change to your deployed API URL

## 📋 Collection Overview

### 🎯 **Dashboard Analytics Endpoints (5 endpoints)**

#### 1. **Get Comprehensive Dashboard Stats**
- **Endpoint**: `GET /admin/stats`
- **Purpose**: Get all dashboard statistics in one call
- **Returns**: Total students, colleges, departments, admins, recognitions
- **Use Case**: Dashboard overview cards/widgets

#### 2. **Get Registration Trends**
- **Endpoint**: `GET /admin/analytics/registration-trends?days=30`
- **Purpose**: Analyze student registration patterns over time
- **Parameters**: `days` (default: 30)
- **Use Case**: Line/bar charts showing registration trends

#### 3. **Get College Distribution**
- **Endpoint**: `GET /admin/analytics/college-distribution`
- **Purpose**: Student distribution across colleges
- **Use Case**: Pie charts showing college enrollment percentages

#### 4. **Get Department Enrollment**
- **Endpoint**: `GET /admin/analytics/department-enrollment?limit=10`
- **Purpose**: Student enrollment by department
- **Parameters**: `limit` (default: 20)
- **Use Case**: Bar charts showing department popularity

#### 5. **Get System Health Metrics**
- **Endpoint**: `GET /admin/analytics/system-health`
- **Purpose**: Performance metrics and system health
- **Use Case**: System monitoring dashboard

### 👤 **Admin Management (1 endpoint)**

#### 6. **Get Admin Users Count**
- **Endpoint**: `GET /admin/users/count`
- **Purpose**: Total admin users count
- **Use Case**: Admin management statistics

## 🧪 Testing Guide

### Automated Testing
1. **Collection Runner**: Use Postman Collection Runner to test all endpoints
2. **Pre/Post Scripts**: Built-in tests validate responses
3. **Environment Variables**: Auto-populated during tests

### Manual Testing
1. **Start with Stats**: Run "Get Comprehensive Dashboard Stats" first
2. **Check Authentication**: Ensure token is valid (401 = expired token)
3. **Validate Data**: Check response structure and data types

## 📊 Response Examples

### Dashboard Stats Response
```json
{
  "message": "Admin statistics retrieved successfully",
  "status_code": 200,
  "count": 1,
  "data": [
    {
      "total_students": 150,
      "total_colleges": 5,
      "total_departments": 25,
      "total_admins": 3,
      "total_recognitions": 1250,
      "recent_recognitions": 45
    }
  ]
}
```

### Registration Trends Response
```json
{
  "message": "Registration trends retrieved successfully",
  "status_code": 200,
  "count": 1,
  "data": [
    {
      "daily_registrations": [
        {"date": "2025-07-04", "count": 5},
        {"date": "2025-07-05", "count": 8},
        {"date": "2025-07-06", "count": 3}
      ],
      "total_period": 45,
      "period_start": "2025-07-04",
      "period_end": "2025-08-03"
    }
  ]
}
```

### College Distribution Response
```json
{
  "message": "College distribution retrieved successfully",
  "status_code": 200,
  "count": 1,
  "data": [
    {
      "college_distribution": [
        {
          "college_id": "uuid-1",
          "college_name": "College of Engineering",
          "student_count": 75,
          "percentage": 50.0
        }
      ],
      "total_students": 150
    }
  ]
}
```

## 🎯 Frontend Integration

### React/JavaScript Example
```javascript
// Dashboard Stats
const fetchDashboardStats = async () => {
  const response = await fetch('/admin/stats', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  
  setDashboardStats({
    students: data.data[0].total_students,
    colleges: data.data[0].total_colleges,
    departments: data.data[0].total_departments,
    admins: data.data[0].total_admins
  });
};

// Registration Trends Chart
const fetchRegistrationTrends = async () => {
  const response = await fetch('/admin/analytics/registration-trends?days=30', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  
  // Perfect for Chart.js or similar
  const chartData = {
    labels: data.data[0].daily_registrations.map(d => d.date),
    datasets: [{
      data: data.data[0].daily_registrations.map(d => d.count),
      label: 'Registrations'
    }]
  };
};

// College Distribution Pie Chart
const fetchCollegeDistribution = async () => {
  const response = await fetch('/admin/analytics/college-distribution', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  
  // Perfect for pie chart
  const pieData = data.data[0].college_distribution.map(college => ({
    label: college.college_name,
    value: college.student_count,
    percentage: college.percentage
  }));
};
```

## 🔧 Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Token expired or invalid
   - Get new token from `/auth/login-otp` → `/auth/verify-login-otp`

2. **500 Internal Server Error**
   - Check server logs
   - Ensure database is running
   - Verify all dependencies are installed

3. **Empty Data Arrays**
   - No data in database yet
   - Use sample creation scripts to populate test data

4. **CORS Issues**
   - Ensure CORS is configured in FastAPI
   - Check allowed origins

### Debug Tips
- Use Postman Console to see request/response details
- Check environment variables are set correctly
- Verify server is running on correct port
- Test basic endpoints first (like `/admin/stats`)

## 📁 Files Included

- `KNUST_Analytics_Dashboard.postman_collection.json` - Main collection
- `KNUST_Analytics_Dashboard.postman_environment.json` - Environment variables
- `ANALYTICS_POSTMAN_GUIDE.md` - This guide

## 🔄 Updates

When new endpoints are added to the API:
1. Update the collection with new requests
2. Add appropriate tests and examples
3. Update this documentation
4. Re-export and distribute

## 📞 Support

For issues with the Postman collection:
1. Check this guide first
2. Verify API server is running
3. Test endpoints individually
4. Check server logs for errors

---

**Happy Testing! 🚀**
