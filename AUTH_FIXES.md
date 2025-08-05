# 🔧 Authentication Issues Fix Guide

## 🚨 **Issues Identified from Logs:**

1. **404 Error:** `/auth/logout` endpoint missing ✅ **FIXED**
2. **422 Errors:** Login endpoints validation issues ✅ **PARTIALLY FIXED**

---

## 🔐 **Updated Authentication Endpoints**

### **1. New Logout Endpoint (ADDED):**
```javascript
// POST /auth/logout
const logout = async () => {
  const response = await fetch('/auth/logout', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  // Remove tokens from local storage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};
```

### **2. JSON Login Endpoint (ADDED):**
```javascript
// POST /auth/login-json (NEW - for JSON payloads)
const loginWithJSON = async (email, password) => {
  const response = await fetch('/auth/login-json', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const result = await response.json();
  if (response.ok) {
    return result; // { access_token, refresh_token, token_type }
  } else {
    throw new Error(result.detail);
  }
};
```

### **3. Form-based Login (EXISTING):**
```javascript
// POST /auth/login (for form data)
const loginWithForm = async (email, password) => {
  const formData = new FormData();
  formData.append('username', email);  // Note: 'username' not 'email'
  formData.append('password', password);
  
  const response = await fetch('/auth/login', {
    method: 'POST',
    body: formData  // No Content-Type header for FormData
  });
};
```

### **4. OTP Login (EXISTING - CHECK PAYLOAD):**
```javascript
// POST /auth/login-otp
const requestOTP = async (email, password) => {
  const response = await fetch('/auth/login-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      email: email,    // Must be valid email format
      password: password 
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    console.error('OTP request failed:', error);
  }
};
```

---

## 🔍 **Debugging 422 Errors**

### **Common Causes:**
1. **Wrong Content-Type:** Using JSON for form endpoints
2. **Missing Fields:** Required fields not provided
3. **Invalid Email Format:** Email validation failing
4. **Password Validation:** Password too short (<8 characters)

### **Debug Steps:**
```javascript
// Add error logging to identify exact validation issues
const debugLogin = async (payload) => {
  try {
    const response = await fetch('/auth/login-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Status:', response.status);
      console.error('Error details:', errorText);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
};

// Test with various payloads
debugLogin({ email: "test@knust.edu.gh", password: "password123" });
```

---

## 📝 **Updated Admin Panel Login Flow**

### **Recommended Flow:**
```javascript
const AdminLogin = () => {
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });

  // Option 1: Direct JSON Login (NEW)
  const handleDirectLogin = async () => {
    try {
      const response = await fetch('/auth/login-json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });
      
      if (response.ok) {
        const tokens = await response.json();
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        // Redirect to dashboard
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  // Option 2: OTP-based Login
  const handleOTPLogin = async () => {
    try {
      // Step 1: Request OTP
      const otpResponse = await fetch('/auth/login-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });
      
      if (otpResponse.ok) {
        // Step 2: Show OTP input, then verify
        const otp = prompt('Enter OTP:');
        const verifyResponse = await fetch('/auth/verify-login-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            email: loginData.email, 
            otp: otp 
          })
        });
        
        if (verifyResponse.ok) {
          const tokens = await verifyResponse.json();
          // Store tokens and redirect
        }
      }
    } catch (error) {
      console.error('OTP login failed:', error);
    }
  };

  return (
    <form>
      <input 
        type="email" 
        value={loginData.email}
        onChange={(e) => setLoginData({...loginData, email: e.target.value})}
        placeholder="Email"
        required
      />
      <input 
        type="password" 
        value={loginData.password}
        onChange={(e) => setLoginData({...loginData, password: e.target.value})}
        placeholder="Password (min 8 chars)"
        required
      />
      
      <button type="button" onClick={handleDirectLogin}>
        Direct Login
      </button>
      <button type="button" onClick={handleOTPLogin}>
        Login with OTP
      </button>
    </form>
  );
};
```

---

## 🚀 **Server Status**

✅ **Server is running** (based on your logs)
✅ **Admin stats endpoint working** (200 OK)
✅ **CORS configured** (OPTIONS requests successful)
✅ **Missing logout endpoint added**
✅ **JSON login endpoint added**

---

## 🎯 **Next Steps**

1. **Update your frontend** to use `/auth/login-json` for JSON payloads
2. **Add proper error handling** to identify specific validation issues
3. **Test with valid email formats** (e.g., admin@knust.edu.gh)
4. **Ensure passwords are ≥8 characters**
5. **Use `/auth/logout` for logout functionality**

The server is running fine - the issues are primarily with how the frontend is calling the authentication endpoints. Use the updated endpoint guide above to fix the 422 errors! 🔧
