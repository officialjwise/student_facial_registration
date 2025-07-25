#!/usr/bin/env python3
"""
Test script to verify the admin stats endpoint fix
"""
import asyncio
import httpx
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
TEST_BASE_URL = "http://localhost:8000"
TEST_ADMIN_EMAIL = "officialjwise20@gmail.com"
TEST_ADMIN_PASSWORD = "your_password_here"  # Update this


async def login_admin():
    """Login and get JWT token."""
    logger.info("Logging in admin...")
    
    async with httpx.AsyncClient() as client:
        # Login
        login_data = {
            "username": TEST_ADMIN_EMAIL,
            "password": TEST_ADMIN_PASSWORD
        }
        
        try:
            response = await client.post(
                f"{TEST_BASE_URL}/auth/login",
                data=login_data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return token_data["access_token"]
            else:
                logger.error(f"Login failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return None


async def test_admin_stats(token):
    """Test the admin stats endpoint."""
    logger.info("Testing admin stats endpoint...")
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = await client.get(
                f"{TEST_BASE_URL}/admin/stats",
                headers=headers,
                timeout=30.0
            )
            
            logger.info(f"Admin stats response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Stats retrieved successfully: {json.dumps(data, indent=2)}")
                return True
            else:
                logger.error(f"Stats request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing admin stats: {str(e)}")
            return False


async def test_recognition_logs(token):
    """Test the recognition logs endpoint."""
    logger.info("Testing recognition logs endpoint...")
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = await client.get(
                f"{TEST_BASE_URL}/admin/recognition-logs",
                headers=headers,
                timeout=30.0
            )
            
            logger.info(f"Recognition logs response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Logs count: {data.get('count', 0)}")
                return True
            else:
                logger.error(f"Logs request failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing recognition logs: {str(e)}")
            return False


async def main():
    """Run all tests."""
    logger.info("Starting admin endpoint tests...")
    
    # Get authentication token
    token = await login_admin()
    if not token:
        logger.error("Failed to get authentication token")
        return
    
    logger.info("Authentication successful!")
    
    # Test admin stats endpoint
    logger.info("\n=== Testing Admin Stats Endpoint ===")
    stats_success = await test_admin_stats(token)
    
    # Test recognition logs endpoint
    logger.info("\n=== Testing Recognition Logs Endpoint ===")
    logs_success = await test_recognition_logs(token)
    
    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Admin Stats: {'✅ PASSED' if stats_success else '❌ FAILED'}")
    logger.info(f"Recognition Logs: {'✅ PASSED' if logs_success else '❌ FAILED'}")
    
    if stats_success and logs_success:
        logger.info("🎉 All tests passed! The admin endpoints are working correctly.")
    else:
        logger.info("⚠️  Some tests failed. Please check the server logs.")


if __name__ == "__main__":
    asyncio.run(main())
