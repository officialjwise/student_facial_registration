import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple
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

def _validate_image_data(image_data: bytes) -> bool:
    """Validate image data format and size."""
    try:
        if len(image_data) == 0:
            return False
        
        # Try to open the image with PIL to validate format
        with Image.open(BytesIO(image_data)) as img:
            # Check if image is too large (> 10MB)
            if len(image_data) > 10 * 1024 * 1024:
                return False
            # Check minimum dimensions
            if img.size[0] < 100 or img.size[1] < 100:
                return False
        return True
    except Exception as e:
        logger.error(f"Image validation failed: {str(e)}")
        return False

def _extract_face_embedding_sync(image_data: bytes) -> Optional[np.ndarray]:
    """Synchronous face embedding extraction (runs in thread pool)."""
    try:
        if not _validate_image_data(image_data):
            logger.warning("Invalid image data provided")
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
    """Extract facial embedding from an image asynchronously."""
    _check_face_recognition_availability()
    
    try:
        # Run the CPU-intensive task in a thread pool
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            face_recognition_executor,
            _extract_face_embedding_sync,
            image_data
        )
        return embedding
        
    except Exception as e:
        logger.error(f"Error in async face embedding extraction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process image for face recognition"
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

async def recognize_face(image_data: bytes) -> Optional[Tuple[int, float]]:
    """Recognize a face by comparing it to stored embeddings."""
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
        
        return result
        
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

# Cleanup function for graceful shutdown
def cleanup_face_recognition():
    """Cleanup face recognition resources."""
    try:
        face_recognition_executor.shutdown(wait=True)
        logger.info("Face recognition executor shut down successfully")
    except Exception as e:
        logger.error(f"Error during face recognition cleanup: {str(e)}")