import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, List, Dict
from io import BytesIO
from uuid import UUID
import numpy as np
from scipy.spatial import KDTree
from fastapi import HTTPException, status
from PIL import Image

# Import face_recognition with proper error handling
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError as e:
    logging.error(f"Face recognition import failed: {str(e)}")
    logging.error("Please install face_recognition_models: pip install git+https://github.com/ageitgey/face_recognition_models")
    FACE_RECOGNITION_AVAILABLE = False

from core.config import settings
from core.supabase import supabase
from crud.students import get_student_by_id

logger = logging.getLogger(__name__)

# Thread pool for CPU-intensive face recognition tasks
face_recognition_executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)

def _check_face_recognition_availability():
    """Check if face recognition is properly installed."""
    if not FACE_RECOGNITION_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Face recognition service is not available. Please install face_recognition_models."
        )

def _validate_image_data(image_data: bytes) -> Tuple[bool, str]:
    """Validate image data format and size."""
    try:
        if not image_data:
            return False, "Empty image data provided"
        
        # Try to open the image with PIL to validate format
        try:
            with Image.open(BytesIO(image_data)) as img:
                # Check if image is too large (> 10MB)
                if len(image_data) > 10 * 1024 * 1024:
                    return False, "Image size too large. Maximum size is 10MB"
                # Check minimum dimensions - face_recognition works well with images as small as 50x50
                if img.size[0] < 50 or img.size[1] < 50:
                    return False, "Image dimensions too small. Minimum size is 50x50 pixels"
                # Validate image format
                if hasattr(img, 'format') and img.format and img.format.lower() not in ['jpeg', 'jpg', 'png']:
                    return False, "Invalid image format. Only JPEG and PNG are supported"
                return True, ""
        except Exception as e:
            return False, f"Invalid image format: {str(e)}"
            
    except Exception as e:
        logger.warning(f"Invalid image data: {str(e)}")
        return False, "Invalid image data provided"

def _extract_face_embedding_sync(image_data: bytes) -> Optional[np.ndarray]:
    """Synchronous face embedding extraction (runs in thread pool)."""
    try:
        is_valid, error_message = _validate_image_data(image_data)
        if not is_valid:
            logger.warning(f"Invalid image data: {error_message}")
            return None
            
        # Load image from bytes
        image = face_recognition.load_image_file(BytesIO(image_data))
        
        # Get face locations first for better performance
        face_locations = face_recognition.face_locations(image, model="hog")
        
        if not face_locations:
            logger.warning("No face detected in provided image")
            return None
            
        if len(face_locations) > 1:
            logger.warning(f"Multiple faces detected ({len(face_locations)}), using the first one")
        
        # Extract encodings for detected faces
        encodings = face_recognition.face_encodings(image, face_locations)
        
        if not encodings:
            logger.warning("No face encodings could be generated")
            return None
            
        logger.info("Face embedding extracted successfully")
        return encodings[0]
        
    except Exception as e:
        logger.error(f"Error extracting face embedding: {str(e)}")
        raise

async def extract_face_embedding(image_data: bytes) -> Optional[np.ndarray]:
    """Extract facial embedding from image data."""
    _check_face_recognition_availability()
    
    # Validate image data
    is_valid, error_message = _validate_image_data(image_data)
    if not is_valid:
        logger.warning(f"Invalid image data: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    try:
        # Load the image and get face encoding
        img = face_recognition.load_image_file(BytesIO(image_data))
        face_locations = await asyncio.get_event_loop().run_in_executor(
            face_recognition_executor, face_recognition.face_locations, img
        )
        
        if not face_locations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image"
            )
            
        if len(face_locations) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multiple faces detected in the image. Please provide an image with a single face"
            )

        face_encodings = await asyncio.get_event_loop().run_in_executor(
            face_recognition_executor, face_recognition.face_encodings, img, face_locations
        )
        
        if not face_encodings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract facial features. Please provide a clearer image"
            )
            
        return face_encodings[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face recognition error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process the image. Please try again with a different image"
        )

def _recognize_face_sync(embedding: np.ndarray, stored_embeddings: list) -> Optional[Tuple[int, float]]:
    """Synchronous face recognition (runs in thread pool)."""
    try:
        if not stored_embeddings:
            logger.info("No stored embeddings for comparison")
            return None
            
        # Prepare data for KDTree
        ids, vectors = zip(*stored_embeddings)
        vectors_array = np.array(vectors)
        
        # Use KDTree for efficient nearest neighbor search
        kdtree = KDTree(vectors_array)
        distance, index = kdtree.query(embedding, k=1)
        
        confidence_threshold = settings.FACE_RECOGNITION_THRESHOLD
        
        if distance < confidence_threshold:
            student_id = ids[index]
            confidence = 1 - distance
            logger.info(f"Face recognized for student ID: {student_id} with confidence: {confidence:.3f}")
            return student_id, distance
        else:
            logger.info(f"No matching face found. Best match distance: {distance:.3f} (threshold: {confidence_threshold})")
            return None
            
    except Exception as e:
        logger.error(f"Error during face recognition comparison: {str(e)}")
        raise

async def recognize_face(image_data: bytes):
    """Recognize a face by comparing it to stored embeddings and return the student."""
    _check_face_recognition_availability()
    
    try:
        # Extract embedding from input image
        embedding = await extract_face_embedding(image_data)
        if embedding is None:
            return None
        
        # Fetch stored embeddings from database
        logger.debug("Fetching stored face embeddings from database")
        response = supabase.table("students").select("id, face_embedding").execute()
        
        if not response.data:
            logger.info("No students found in database for recognition")
            return None
        
        # Filter out students without face embeddings
        stored_embeddings = []
        for record in response.data:
            if record.get("face_embedding"):
                try:
                    embedding_array = np.array(record["face_embedding"])
                    if embedding_array.shape == (128,):  # Standard face_recognition embedding size
                        stored_embeddings.append((record["id"], embedding_array))
                except Exception as e:
                    logger.warning(f"Invalid embedding for student ID {record['id']}: {str(e)}")
                    continue
        
        if not stored_embeddings:
            logger.info("No valid face embeddings found in database")
            return None
        
        logger.info(f"Comparing against {len(stored_embeddings)} stored face embeddings")
        
        # Run face recognition in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            face_recognition_executor,
            _recognize_face_sync,
            embedding,
            stored_embeddings
        )
        
        if result:
            student_id, distance = result
            # Get the full student record
            student = await get_student_by_id(UUID(student_id))
            return student
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during face recognition: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face recognition service temporarily unavailable"
        )

async def store_face_embedding(student_id: UUID, image_data: bytes) -> bool:
    """Store face embedding for a student."""
    try:
        embedding = await extract_face_embedding(image_data)
        if embedding is None:
            return False
        
        # Convert numpy array to list for JSON storage
        embedding_list = embedding.tolist()
        
        # Update student record with face embedding
        response = supabase.table("students").update({
            "face_embedding": embedding_list
        }).eq("id", str(student_id)).execute()
        
        if response.data:
            logger.info(f"Face embedding stored successfully for student ID: {student_id}")
            return True
        else:
            logger.error(f"Failed to store face embedding for student ID: {student_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error storing face embedding: {str(e)}")
        return False

async def detect_faces_with_bounding_boxes(image_data: bytes) -> Dict:
    """
    Detect faces in image and return bounding box coordinates.
    
    Returns:
        Dict containing:
        - faces_detected: number of faces found
        - face_locations: list of bounding box coordinates [(top, right, bottom, left), ...]
        - image_dimensions: (width, height) of the image
        - face_encodings: facial embeddings if faces found
    """
    _check_face_recognition_availability()
    
    # Validate image data
    is_valid, error_message = _validate_image_data(image_data)
    if not is_valid:
        logger.warning(f"Invalid image data: {error_message}")
        return {
            "faces_detected": 0,
            "face_locations": [],
            "image_dimensions": (0, 0),
            "face_encodings": [],
            "error": error_message
        }

    try:
        # Load the image
        img = face_recognition.load_image_file(BytesIO(image_data))
        
        # Get image dimensions
        height, width = img.shape[:2]
        
        # Find face locations
        face_locations = await asyncio.get_event_loop().run_in_executor(
            face_recognition_executor, face_recognition.face_locations, img
        )
        
        # Get face encodings if faces are found
        face_encodings = []
        if face_locations:
            face_encodings = await asyncio.get_event_loop().run_in_executor(
                face_recognition_executor, face_recognition.face_encodings, img, face_locations
            )
        
        # Convert face_encodings to lists for JSON serialization
        face_encodings_list = [encoding.tolist() for encoding in face_encodings]
        
        return {
            "faces_detected": len(face_locations),
            "face_locations": face_locations,  # [(top, right, bottom, left), ...]
            "image_dimensions": (width, height),
            "face_encodings": face_encodings_list
        }
        
    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return {
            "faces_detected": 0,
            "face_locations": [],
            "image_dimensions": (0, 0),
            "face_encodings": [],
            "error": f"Face detection failed: {str(e)}"
        }

async def extract_face_embedding_with_bbox(image_data: bytes) -> Tuple[Optional[np.ndarray], Dict]:
    """
    Extract facial embedding and return bounding box information.
    
    Returns:
        Tuple of (face_embedding, bounding_box_info)
    """
    detection_result = await detect_faces_with_bounding_boxes(image_data)
    
    if detection_result["faces_detected"] == 0:
        return None, detection_result
    
    if detection_result["faces_detected"] > 1:
        detection_result["error"] = "Multiple faces detected. Please provide an image with a single face."
        return None, detection_result
    
    # Return the first (and only) face encoding as numpy array
    if detection_result["face_encodings"]:
        face_embedding = np.array(detection_result["face_encodings"][0])
        return face_embedding, detection_result
    
    return None, detection_result

# Cleanup function for graceful shutdown
def cleanup_face_recognition():
    """Cleanup face recognition resources."""
    try:
        face_recognition_executor.shutdown(wait=True)
        logger.info("Face recognition executor shut down successfully")
    except Exception as e:
        logger.error(f"Error during face recognition cleanup: {str(e)}")

async def recognize_face_from_base64(image_data: bytes):
    """
    Recognize a face from base64-decoded image data.
    This is a wrapper around the existing recognize_face function.
    """
    return await recognize_face(image_data)