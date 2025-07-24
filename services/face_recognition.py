import face_recognition
import numpy as np
from scipy.spatial import KDTree
from models.database import supabase
from fastapi import HTTPException, status
from typing import Optional, Tuple
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

async def extract_face_embedding(image_data: bytes) -> Optional[np.ndarray]:
    """Extract facial embedding from an image."""
    try:
        image = face_recognition.load_image_file(BytesIO(image_data))
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            logger.warning("No face detected in provided image")
            return None
        return encodings[0]
    except Exception as e:
        logger.error(f"Error extracting face embedding: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image data")

async def recognize_face(image_data: bytes) -> Optional[Tuple[int, float]]:
    """Recognize a face by comparing it to stored embeddings."""
    try:
        embedding = await extract_face_embedding(image_data)
        if not embedding:
            return None

        response = supabase.table("students").select("id, face_embedding").execute()
        if not response.data:
            logger.info("No students found in database for recognition")
            return None

        embeddings = [(r["id"], np.array(r["face_embedding"])) for r in response.data]
        ids, vectors = zip(*embeddings)
        kdtree = KDTree(vectors)
        distance, index = kdtree.query(embedding)

        if distance < 0.6:  # Confidence threshold
            logger.info(f"Face recognized for student ID: {ids[index]} with confidence: {1 - distance}")
            return ids[index], distance
        logger.info("No matching face found")
        return None
    except Exception as e:
        logger.error(f"Error during face recognition: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Face recognition failed")