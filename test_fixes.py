#!/usr/bin/env python3
"""
Test script to verify the fixes for image validation and face recognition
"""
import asyncio
import base64
import httpx
import json
from io import BytesIO
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
TEST_BASE_URL = "http://localhost:8000"
TEST_ADMIN_EMAIL = "officialjwise20@gmail.com"
TEST_ADMIN_PASSWORD = "your_password_here"  # Update this


async def create_test_image(width: int, height: int, format: str = "JPEG") -> bytes:
    """Create a test image with specified dimensions."""
    img = Image.new('RGB', (width, height), color='red')
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


async def test_image_validation():
    """Test different image scenarios."""
    logger.info("Testing image validation...")
    
    # Test 1: Valid image (100x100)
    valid_image = await create_test_image(100, 100)
    logger.info(f"Created valid test image: {len(valid_image)} bytes")
    
    # Test 2: Small image (30x30) - should fail
    small_image = await create_test_image(30, 30)
    logger.info(f"Created small test image: {len(small_image)} bytes")
    
    # Test 3: Large valid image (200x200)
    large_image = await create_test_image(200, 200)
    logger.info(f"Created large test image: {len(large_image)} bytes")
    
    return valid_image, small_image, large_image


async def test_face_recognition_upload(image_data: bytes):
    """Test face recognition with file upload."""
    logger.info("Testing face recognition upload...")
    
    async with httpx.AsyncClient() as client:
        files = {
            'image': ('test.jpg', image_data, 'image/jpeg')
        }
        
        try:
            response = await client.post(
                f"{TEST_BASE_URL}/students/recognize",
                files=files,
                timeout=30.0
            )
            
            logger.info(f"Recognition response status: {response.status_code}")
            logger.info(f"Recognition response: {response.text[:200]}...")
            
            return response.status_code, response.json() if response.status_code != 422 else response.text
            
        except Exception as e:
            logger.error(f"Error testing face recognition: {str(e)}")
            return 500, str(e)


async def test_base64_validation():
    """Test base64 image validation."""
    logger.info("Testing base64 validation...")
    
    # Test with different base64 scenarios
    valid_image = await create_test_image(100, 100)
    valid_b64 = base64.b64encode(valid_image).decode('utf-8')
    
    # Test with data URL prefix
    data_url_b64 = f"data:image/jpeg;base64,{valid_b64}"
    
    # Test with invalid base64
    invalid_b64 = "invalid_base64_string"
    
    # Test with empty base64
    empty_b64 = ""
    
    test_cases = [
        ("valid_b64", valid_b64),
        ("data_url_b64", data_url_b64), 
        ("invalid_b64", invalid_b64),
        ("empty_b64", empty_b64)
    ]
    
    return test_cases


async def main():
    """Run all tests."""
    logger.info("Starting image validation and face recognition tests...")
    
    # Test image creation
    valid_image, small_image, large_image = await test_image_validation()
    
    # Test face recognition with different image sizes
    logger.info("\n=== Testing Face Recognition Upload ===")
    
    # Test with valid image
    status, response = await test_face_recognition_upload(valid_image)
    logger.info(f"Valid image (100x100): Status {status}")
    
    # Test with small image (should give 422 or 400)
    status, response = await test_face_recognition_upload(small_image)
    logger.info(f"Small image (30x30): Status {status}")
    
    # Test with large image
    status, response = await test_face_recognition_upload(large_image)
    logger.info(f"Large image (200x200): Status {status}")
    
    # Test base64 validation
    logger.info("\n=== Testing Base64 Validation ===")
    test_cases = await test_base64_validation()
    for case_name, b64_data in test_cases:
        logger.info(f"Test case: {case_name} - Length: {len(b64_data)}")
    
    logger.info("\nTests completed!")


if __name__ == "__main__":
    asyncio.run(main())
