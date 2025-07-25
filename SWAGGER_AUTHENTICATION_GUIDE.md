# 🎓 KNUST Student System API - Swagger Documentation Guide

## 🔐 How to Authenticate in Swagger UI

### Step 1: Access the Documentation
1. Start your FastAPI server: `uvicorn main:app --reload`
2. Open your browser and go to: `http://localhost:8000/docs`
3. You'll see the enhanced Swagger UI with custom KNUST styling

### Step 2: Register an Admin Account
1. **Find the Authentication section** (🔐 Authentication)
2. **Click on `POST /auth/register`**
3. **Click "Try it out"**
4. **Enter your details in the request body:**
   ```json
   {
     "email": "your.email@knust.edu.gh",
     "password": "YourSecurePassword123!"
   }
   ```
5. **Click "Execute"**
6. **Check your email** for the 6-digit OTP code

### Step 3: Verify Your Account
1. **Click on `POST /auth/verify-otp`**
2. **Click "Try it out"**
3. **Enter the verification details:**
   ```json
   {
     "email": "your.email@knust.edu.gh", 
     "otp": "123456"
   }
   ```
4. **Click "Execute"**
5. You should see: `"message": "Account verified successfully"`

### Step 4: Login and Get Your Token

#### Option A: OTP Login (Recommended)
1. **Click on `POST /auth/login-otp`**
2. **Enter your credentials:**
   ```json
   {
     "email": "your.email@knust.edu.gh",
     "password": "YourSecurePassword123!"
   }
   ```
3. **Check your email** for the login OTP
4. **Click on `POST /auth/verify-login-otp`**
5. **Enter the OTP:**
   ```json
   {
     "email": "your.email@knust.edu.gh",
     "otp": "654321"
   }
   ```
6. **Copy the `access_token`** from the response

#### Option B: Direct Login
1. **Click on `POST /auth/login`**
2. **Enter form data:**
   - username: `your.email@knust.edu.gh`
   - password: `YourSecurePassword123!`
3. **Copy the `access_token`** from the response

### Step 5: Authorize in Swagger
1. **Look for the 🔒 "Authorize" button** at the top of the page
2. **Click the "Authorize" button**
3. **In the "BearerAuth" field, enter:**
   ```
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   *(Replace with your actual token, include "Bearer " prefix)*
4. **Click "Authorize"**
5. **Click "Close"**

### Step 6: Test Protected Endpoints
- You can now test all endpoints marked with 🔒 **Protected**
- Public endpoints (🔓 **Public**) work without authentication
- Try testing some admin endpoints like:
  - `GET /admin/stats`
  - `GET /admin/students`
  - `POST /colleges/`

## 🎨 Custom Interface Features

### Enhanced Visual Design
- **Custom KNUST Color Scheme**: Blue, green, and gold branding
- **Gradient Backgrounds**: Modern gradient designs throughout
- **Emoji Icons**: Clear visual indicators for different sections
- **Responsive Design**: Works great on mobile and desktop

### Authentication Indicators
- **🔓 Public Badge**: Endpoints that don't require authentication
- **🔒 Protected Badge**: Endpoints that require JWT tokens
- **Color-coded Methods**: Different colors for GET, POST, PUT, DELETE
- **Hover Effects**: Interactive elements with smooth transitions

### Improved Documentation
- **Step-by-step Auth Guide**: Clear instructions in the description
- **Enhanced Descriptions**: Better endpoint documentation
- **Quick Start Section**: Fast track to get testing
- **Token Management Info**: Refresh token usage explained

### Custom Styling Elements
- **Branded Header**: KNUST-themed top banner
- **Custom CSS**: Professional styling with animations
- **Enhanced Buttons**: Improved authorize and execute buttons
- **Better Code Blocks**: Syntax-highlighted request/response examples

## 🔄 Token Management

### Access Token
- **Duration**: 30 minutes
- **Usage**: Include in Authorization header as `Bearer <token>`
- **Renewal**: Use refresh token before expiry

### Refresh Token  
- **Duration**: 7 days
- **Usage**: Use `POST /auth/refresh` endpoint
- **Security**: Store securely, don't expose in client-side code

### Token Refresh Process
1. **When access token expires**, use the refresh endpoint
2. **Click on `POST /auth/refresh`**
3. **Enter your refresh token:**
   ```json
   {
     "refresh_token": "your_refresh_token_here"
   }
   ```
4. **Get new tokens** and update your authorization

## 🚀 Quick Testing Sequence

### For First-Time Users:
1. Register → Verify → Login → Authorize → Test!

### For Return Users:
1. Login → Authorize → Test!
2. Or use refresh token if access token expired

## 📱 Endpoint Categories

### 🔓 Public Endpoints (No Auth Required)
- `GET /` - Health check
- `POST /auth/*` - All authentication endpoints
- `GET /colleges/` - List colleges
- `GET /departments/` - List departments  
- `POST /students/` - Student registration
- `POST /students/recognize` - Face recognition

### 🔒 Protected Endpoints (Require JWT)
- `GET /admin/*` - Admin dashboard and management
- `POST /colleges/` - Create college
- `PUT/DELETE /colleges/*` - Modify colleges
- `POST /departments/` - Create department
- `PUT/DELETE /departments/*` - Modify departments
- `GET /students/*` - View students (admin)
- `PUT/DELETE /students/*` - Modify students
- `POST /students/admin/create` - Admin-create student

## 🛠️ Troubleshooting

### Common Issues:

1. **"401 Unauthorized" Error**
   - Check if your token is correctly formatted: `Bearer <token>`
   - Verify token hasn't expired (30 minutes)
   - Ensure you clicked "Authorize" after getting the token

2. **"Invalid Token" Error**  
   - Token may be expired, get a new one via login
   - Check for typos in the token
   - Make sure you included "Bearer " prefix

3. **OTP Not Received**
   - Check spam/junk folder
   - Verify email address is correct
   - OTP expires in 5 minutes

4. **Can't See Custom Styling**
   - Ensure `/static/swagger-ui-custom.css` file exists
   - Check browser developer tools for CSS loading errors
   - Try hard refresh (Ctrl+F5 or Cmd+Shift+R)

### Getting Help:
- Check the browser console for JavaScript errors
- Verify your server is running on the correct port
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## 🎯 Pro Tips

1. **Save Your Tokens**: Copy and save tokens for extended testing sessions
2. **Use Refresh Wisely**: Set up refresh token handling in your frontend
3. **Test Public First**: Start with public endpoints to verify basic functionality
4. **Monitor Token Expiry**: Watch for 401 errors indicating token expiration
5. **Use Environment Variables**: Store tokens in Postman environment for easier management

This enhanced Swagger documentation provides a professional, branded, and user-friendly interface for testing your KNUST Student System API! 🎓✨
