# 📱 React.js Integration Guide for KNUST Student System

## 🎯 **API Endpoints for Frontend Integration**

### **Base URL:** `http://localhost:8000`

---

## 1. **Student Registration with Optional Photo**

### **Endpoint:** `POST /students/`

```javascript
const registerStudent = async (formData, capturedImage = null) => {
  const payload = {
    student_id: formData.student_id,        // 8 digits
    first_name: formData.first_name,
    last_name: formData.last_name,
    email: formData.email,
    index_number: formData.index_number,    // 10 digits
    phone_number: formData.phone_number,
    date_of_birth: formData.date_of_birth,  // YYYY-MM-DD
    gender: formData.gender,
    program: formData.program,
    level: formData.level,
    college_id: "123e4567-e89b-12d3-a456-426614174000",
    department_id: "223e4567-e89b-12d3-a456-426614174000"
  };

  // Add face image only if captured
  if (capturedImage) {
    payload.face_image = capturedImage; // base64 string with data URL prefix
  }

  try {
    const response = await fetch('http://localhost:8000/students/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();
    
    if (response.ok) {
      // Success: result.data[0] contains student info
      console.log('Student registered:', result.data[0]);
      return { success: true, data: result.data[0] };
    } else {
      // Error: result.detail contains error message
      return { success: false, error: result.detail };
    }
  } catch (error) {
    return { success: false, error: 'Network error' };
  }
};
```

---

## 2. **Face Detection with Bounding Box (NEW)**

### **Endpoint:** `POST /students/detect-face`

```javascript
const detectFacesWithBoundingBox = async (imageDataUrl) => {
  try {
    const response = await fetch('http://localhost:8000/students/detect-face', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        face_image: imageDataUrl  // base64 image with data URL prefix
      })
    });

    const result = await response.json();
    
    if (response.ok) {
      const detectionData = result.data[0];
      return {
        success: true,
        faces_detected: detectionData.faces_detected,
        face_locations: detectionData.face_locations,      // [(top, right, bottom, left), ...]
        image_dimensions: detectionData.image_dimensions,  // [width, height]
        face_encodings: detectionData.face_encodings       // facial embeddings
      };
    } else {
      return { success: false, error: result.detail };
    }
  } catch (error) {
    return { success: false, error: 'Network error' };
  }
};
```

---

## 3. **Face Recognition (Identify Student)**

### **Endpoint:** `POST /students/recognize`

```javascript
const recognizeStudent = async (imageDataUrl) => {
  try {
    const response = await fetch('http://localhost:8000/students/recognize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        face_image: imageDataUrl
      })
    });

    const result = await response.json();
    
    if (response.ok) {
      return {
        success: true,
        student: result.data[0],
        confidence: result.data[0].confidence || 0.0
      };
    } else {
      return { success: false, error: result.detail };
    }
  } catch (error) {
    return { success: false, error: 'Network error' };
  }
};
```

---

## 🎨 **React Component for Face Bounding Box**

```jsx
import React, { useRef, useEffect, useState } from 'react';

const FaceDetectionCanvas = ({ 
  videoRef, 
  imageDataUrl, 
  onFaceDetected 
}) => {
  const canvasRef = useRef(null);
  const [faceBoxes, setFaceBoxes] = useState([]);
  const [isDetecting, setIsDetecting] = useState(false);

  // Detect faces and draw bounding boxes
  const detectAndDrawFaces = async () => {
    if (!imageDataUrl || isDetecting) return;
    
    setIsDetecting(true);
    
    try {
      const detection = await detectFacesWithBoundingBox(imageDataUrl);
      
      if (detection.success) {
        setFaceBoxes(detection.face_locations);
        drawBoundingBoxes(detection.face_locations, detection.image_dimensions);
        
        if (onFaceDetected) {
          onFaceDetected({
            count: detection.faces_detected,
            locations: detection.face_locations
          });
        }
      }
    } catch (error) {
      console.error('Face detection error:', error);
    } finally {
      setIsDetecting(false);
    }
  };

  // Draw bounding boxes on canvas
  const drawBoundingBoxes = (faceLocations, imageDimensions) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const [imageWidth, imageHeight] = imageDimensions;
    
    // Set canvas size to match image
    canvas.width = imageWidth;
    canvas.height = imageHeight;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw bounding boxes
    faceLocations.forEach((location, index) => {
      const [top, right, bottom, left] = location;
      
      // Calculate box dimensions
      const boxWidth = right - left;
      const boxHeight = bottom - top;
      
      // Draw rectangle
      ctx.strokeStyle = '#00ff00';  // Green color
      ctx.lineWidth = 3;
      ctx.strokeRect(left, top, boxWidth, boxHeight);
      
      // Draw label
      ctx.fillStyle = '#00ff00';
      ctx.font = '16px Arial';
      ctx.fillText(`Face ${index + 1}`, left, top - 10);
    });
  };

  // Auto-detect faces when image changes
  useEffect(() => {
    if (imageDataUrl) {
      detectAndDrawFaces();
    }
  }, [imageDataUrl]);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      {/* Canvas overlay for bounding boxes */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          pointerEvents: 'none',
          zIndex: 10
        }}
      />
      
      {/* Face detection status */}
      {isDetecting && (
        <div style={{
          position: 'absolute',
          top: 10,
          right: 10,
          background: 'rgba(0,0,0,0.7)',
          color: 'white',
          padding: '5px 10px',
          borderRadius: '5px',
          zIndex: 20
        }}>
          Detecting faces...
        </div>
      )}
      
      {faceBoxes.length > 0 && (
        <div style={{
          position: 'absolute',
          bottom: 10,
          left: 10,
          background: 'rgba(0,255,0,0.8)',
          color: 'white',
          padding: '5px 10px',
          borderRadius: '5px',
          zIndex: 20
        }}>
          {faceBoxes.length} face{faceBoxes.length !== 1 ? 's' : ''} detected
        </div>
      )}
    </div>
  );
};

export default FaceDetectionCanvas;
```

---

## 🎯 **Complete Integration Example**

```jsx
import React, { useState, useRef } from 'react';
import FaceDetectionCanvas from './FaceDetectionCanvas';

const StudentRegistrationWithFaceDetection = () => {
  const [capturedImage, setCapturedImage] = useState(null);
  const [faceDetectionResult, setFaceDetectionResult] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const capturePhotoWithFaceDetection = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (video && canvas) {
      const ctx = canvas.getContext('2d');
      canvas.width = 640;
      canvas.height = 480;
      ctx.drawImage(video, 0, 0, 640, 480);
      
      const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
      setCapturedImage(imageDataUrl);
      
      // Automatically detect faces after capture
      const detection = await detectFacesWithBoundingBox(imageDataUrl);
      setFaceDetectionResult(detection);
    }
  };

  const handleFaceDetected = (faceInfo) => {
    console.log('Faces detected:', faceInfo);
    // Update UI based on face detection results
  };

  return (
    <div className="registration-container">
      <div className="camera-section">
        <div style={{ position: 'relative' }}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{
              width: '640px',
              height: '480px',
              display: capturedImage ? 'none' : 'block'
            }}
          />
          
          {capturedImage && (
            <div style={{ position: 'relative' }}>
              <img
                src={capturedImage}
                alt="Captured"
                style={{ width: '640px', height: '480px' }}
              />
              <FaceDetectionCanvas
                videoRef={videoRef}
                imageDataUrl={capturedImage}
                onFaceDetected={handleFaceDetected}
              />
            </div>
          )}
          
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
        
        <div className="camera-controls">
          <button onClick={capturePhotoWithFaceDetection}>
            📸 Capture with Face Detection
          </button>
        </div>
        
        {faceDetectionResult && (
          <div className="detection-results">
            <p>
              {faceDetectionResult.faces_detected > 0 
                ? `✅ ${faceDetectionResult.faces_detected} face(s) detected!`
                : '⚠️ No faces detected in image'
              }
            </p>
          </div>
        )}
      </div>
      
      {/* Rest of your registration form */}
    </div>
  );
};

export default StudentRegistrationWithFaceDetection;
```

---

## 🔧 **Key Implementation Notes:**

### **Bounding Box Coordinates:**
- Format: `[top, right, bottom, left]` in pixels
- Origin: Top-left corner of image (0,0)
- Use these coordinates to draw rectangles over detected faces

### **Face Detection Flow:**
1. **Capture/Upload Image** → Get base64 data URL
2. **Call `/students/detect-face`** → Get bounding box coordinates  
3. **Draw Bounding Boxes** → Visual feedback to user
4. **Register Student** → Call `/students/` with confirmed image

### **Error Handling:**
- No faces detected: Allow registration without face data
- Multiple faces: Show warning, ask user to retake
- Network errors: Provide fallback options

### **Performance Tips:**
- Debounce face detection calls (don't call on every frame)
- Show loading states during detection
- Cache detection results to avoid repeated API calls

This setup gives you real-time face detection with visual bounding box feedback, perfect for both registration and recognition workflows!
