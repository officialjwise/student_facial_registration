from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from api.routers import students, auth, admin, colleges, departments, exam_rooms
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    yield
    # You can add shutdown logic here if needed

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="🎓 KNUST Student System API",
        version="1.0.0",
        description="""
## 🎯 KNUST Student Registration and Recognition System

A comprehensive RESTful API for student registration, facial recognition, and administrative management.

### 👥 Development Team

**Group Members:**
1. **Festus Mensah** - 8556221
2. **Eleanor Annang** - 8534421  
3. **Silas Amoakowah Ofosu** - 8532621

### 🔐 Authentication
- Use JWT Bearer tokens for protected endpoints
- Click 🔒 **Authorize** button and enter: `Bearer YOUR_TOKEN`
- Get tokens via `/auth/login` or `/auth/login-otp` → `/auth/verify-login-otp`

### 📋 Endpoint Types
- 🔓 **Public**: Student registration, face recognition, view data
- 🔒 **Protected**: Admin operations, student management

### 📱 Response Format
```json
{
  "message": "Success description",
  "status_code": 200,
  "count": 1,
  "data": [/* response data */]
}
```
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": """
**JWT Bearer Token Authentication**

Format: `Bearer <your-access-token>`

**How to get your token:**
1. Register admin account: `POST /auth/register`
2. Verify with OTP: `POST /auth/verify-otp` 
3. Login: `POST /auth/login-otp` → `POST /auth/verify-login-otp`
4. Copy `access_token` from response
5. Use it here with "Bearer " prefix

**Example:** `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
            """
        }
    }
    
    # Add security requirement to protected endpoints
    for path, path_item in openapi_schema["paths"].items():
        for method, operation in path_item.items():
            # Skip OPTIONS method
            if method == "options":
                continue
                
            # Public endpoints (no auth required)
            public_endpoints = [
                ("/", "get"),
                ("/auth/register", "post"),
                ("/auth/verify-otp", "post"),
                ("/auth/login", "post"),
                ("/auth/login-otp", "post"),
                ("/auth/verify-login-otp", "post"),
                ("/auth/refresh", "post"),
                ("/colleges/", "get"),
                ("/departments/", "get"),
                ("/students/", "post"),
                ("/students/recognize", "post"),
                ("/exam-room/mappings", "get"),
                ("/exam-room/validate", "post")
            ]
            
            # Add security requirement for protected endpoints
            if (path, method) not in public_endpoints:
                operation["security"] = [{"BearerAuth": []}]
                
                # Add security note to description
                if "description" in operation:
                    operation["description"] += "\n\n🔒 **Requires Authentication**: Include JWT token in Authorization header"
                else:
                    operation["description"] = "🔒 **Requires Authentication**: Include JWT token in Authorization header"
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="🎓 KNUST Student System API",
    description="Advanced RESTful API for student registration and facial recognition with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "🔐 Authentication",
            "description": "Admin registration, OTP verification, login, and token management operations"
        },
        {
            "name": "🎓 Students", 
            "description": "Student registration (public), management (admin), and face recognition operations"
        },
        {
            "name": "🏫 Colleges",
            "description": "College management operations - viewing is public, management requires admin auth"
        },
        {
            "name": "🏛️ Departments", 
            "description": "Department management operations - viewing is public, management requires admin auth"
        },
        {
            "name": "🏛️ Exam Room Management",
            "description": "Exam room assignment, management, and real-time student validation operations"
        },
        {
            "name": "👤 Admin",
            "description": "Admin dashboard, statistics, logs, and administrative management operations"
        },
        {
            "name": "❤️ Health",
            "description": "System health check and API status endpoints"
        }
    ]
)

# Mount static files for custom CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set custom OpenAPI schema
app.openapi = custom_openapi

# Custom Swagger UI HTML with enhanced styling
def custom_swagger_ui_html():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎓 KNUST Student System API - Documentation</title>
        <link rel="stylesheet" type="text/css" href="/static/swagger-ui-custom.css" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎓</text></svg>">
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            
            /* Add custom banner */
            .custom-banner {{
                background: linear-gradient(135deg, #1e40af 0%, #059669 100%);
                color: white;
                padding: 20px;
                text-align: center;
                font-size: 1.2rem;
                font-weight: 600;
                border-bottom: 3px solid #f59e0b;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .auth-reminder {{
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border: 2px solid #f59e0b;
                border-radius: 12px;
                padding: 15px;
                margin: 20px;
                text-align: center;
                font-weight: 600;
                color: #92400e;
            }}
        </style>
    </head>
    <body>
        <div class="custom-banner">
            🎓 KNUST Student Registration & Recognition System API
            <br>
            <small>Developed by: Festus Mensah, Eleanor Annang, Silas Amoakowah Ofosu</small>
        </div>
        
        <div class="auth-reminder">
            💡 <strong>Quick Start:</strong> Register → Verify → Login → Click "🔒 Authorize" → Test!
        </div>
        
        <div id="swagger-ui"></div>
        
        <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({{
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                layout: "BaseLayout",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                defaultModelsExpandDepth: 2,
                defaultModelExpandDepth: 2,
                displayOperationId: false,
                tryItOutEnabled: true,
                requestInterceptor: function(req) {{
                    // Add custom headers or modify requests if needed
                    return req;
                }},
                responseInterceptor: function(res) {{
                    // Handle responses if needed  
                    return res;
                }},
                onComplete: function() {{
                    console.log("🎓 KNUST Student System API Documentation Loaded!");
                    
                    // Add custom JavaScript enhancements
                    setTimeout(function() {{
                        // Add public/protected badges
                        const publicPaths = [
                            '/auth/', '/colleges/ GET', '/departments/ GET', 
                            '/students/ POST', '/students/recognize POST', '/ GET'
                        ];
                        
                        document.querySelectorAll('.opblock').forEach(function(block) {{
                            const method = block.querySelector('.opblock-summary-method');
                            const path = block.querySelector('.opblock-summary-path');
                            
                            if (method && path) {{
                                const methodText = method.textContent.trim();
                                const pathText = path.textContent.trim();
                                const isPublic = publicPaths.some(p => 
                                    pathText.includes(p.split(' ')[0]) && 
                                    (p.split(' ')[1] === undefined || methodText === p.split(' ')[1])
                                );
                                
                                // Remove existing badges
                                const existingBadge = block.querySelector('.auth-badge');
                                if (existingBadge) existingBadge.remove();
                                
                                // Add new badge
                                const badge = document.createElement('span');
                                badge.className = 'auth-badge';
                                badge.style.cssText = `
                                    display: inline-block;
                                    padding: 4px 8px;
                                    border-radius: 4px;
                                    font-size: 0.7rem;
                                    font-weight: 600;
                                    margin-left: 10px;
                                    float: right;
                                `;
                                
                                if (isPublic || pathText.includes('/auth/')) {{
                                    badge.textContent = '🔓 Public';
                                    badge.style.background = '#059669';
                                    badge.style.color = 'white';
                                }} else {{
                                    badge.textContent = '🔒 Protected';
                                    badge.style.background = '#dc2626';
                                    badge.style.color = 'white';
                                }}
                                
                                const summary = block.querySelector('.opblock-summary');
                                if (summary) summary.appendChild(badge);
                            }}
                        }});
                    }}, 1000);
                }}
            }});
        </script>
    </body>
    </html>
    """

# Custom endpoint to serve enhanced Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return HTMLResponse(custom_swagger_ui_html())

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8081"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(students.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(colleges.router)
app.include_router(departments.router)
app.include_router(exam_rooms.router)

@app.get("/", tags=["❤️ Health"])
async def root():
    """Root endpoint for health check."""
    logger.info("Root endpoint accessed")
    return {"message": "🎓 KNUST Student Registration and Recognition System - API is running! 🚀"}
