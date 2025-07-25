#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth import register_admin
from schemas.auth import AdminCreate

async def test_registration():
    """Test admin registration with a new email."""
    
    # Create test admin data with unique email
    import time
    unique_email = f"test.admin.{int(time.time())}@example.com"
    test_admin = AdminCreate(
        email=unique_email,
        password="testpassword123"
    )
    
    try:
        print(f"Testing registration for: {test_admin.email}")
        result = await register_admin(test_admin)
        print(f"Registration successful: {result}")
        return True
    except Exception as e:
        print(f"Registration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_registration())
    sys.exit(0 if success else 1)
