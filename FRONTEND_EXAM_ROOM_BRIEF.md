# 🎨 Frontend Development Brief: Exam Room Management UI

## 📋 Project Overview

You need to implement a comprehensive **Exam Room Management System** for the KNUST Student Registration and Recognition System. This system allows administrators to assign students to examination rooms based on their index number ranges and provides real-time validation during exams.

## 🎯 Core Functionality Required

### **System Logic**
- **Index-Based Assignment**: Students are automatically assigned to rooms based on their index number ranges
- **Example**: Index range `8551521 - 8552721` assigns all students with index numbers in this range to room `FF1`
- **Real-time Validation**: During exams, students scan their faces to verify they're in the correct room
- **Audio Feedback**: Success = confirmation beep, Error = warning beep

---

## 🔧 **API Endpoints Available**

### **Admin Endpoints (Require JWT Token)**
```javascript
// Preview assignment before creating room
GET /exam-room/assignments/preview?index_start=8551521&index_end=8552721
Headers: { Authorization: 'Bearer {token}' }

// Create room assignment  
POST /exam-room/assign
Headers: { Authorization: 'Bearer {token}', Content-Type: 'application/json' }
Body: {
  room_code: "FF1",
  room_name: "Engineering Hall 1", 
  index_start: "8551521",
  index_end: "8552721",
  capacity: 50,
  description: "Engineering students hall"
}

// Get all rooms with student counts
GET /exam-room/mappings

// Get room details with student list
GET /exam-room/mappings/{room_id}/students
Headers: { Authorization: 'Bearer {token}' }

// Update room
PUT /exam-room/assign/{room_id}
Headers: { Authorization: 'Bearer {token}' }

// Delete room
DELETE /exam-room/assign/{room_id}
Headers: { Authorization: 'Bearer {token}' }
```

### **Public Endpoints**
```javascript
// Face recognition validation (MOST IMPORTANT)
POST /exam-room/recognize
Body: {
  face_image: "base64_encoded_image",
  room_code: "FF1"
}

// Quick index validation
GET /exam-room/validate/{room_code}/{index_number}
```

---

## 🎨 **UI Components to Build**

### **1. Admin Dashboard - Room Management Panel**

#### **Room Assignment Form**
```jsx
const RoomAssignmentForm = () => {
  // Fields needed:
  // - room_code (e.g., "FF1", "LAB_01")
  // - room_name (e.g., "Engineering Hall 1")
  // - index_start (e.g., "8551521") 
  // - index_end (e.g., "8552721")
  // - capacity (number)
  // - description (optional)
  
  // Features needed:
  // 1. Preview button - shows how many students will be assigned
  // 2. Validation - prevent overlapping index ranges
  // 3. Confirmation dialog before creating
  // 4. Success message with student count
}
```

#### **Room Management Table**
```jsx
const RoomManagementTable = () => {
  // Columns needed:
  // - Room Code | Room Name | Index Range | Assigned Students | Capacity | Utilization | Actions
  
  // Features needed:
  // 1. Display student count vs capacity (45/50)
  // 2. Color coding: Green (normal), Red (overcapacity)
  // 3. Utilization percentage bar
  // 4. Actions: View Students, Edit, Delete
  // 5. Real-time refresh of student counts
}
```

#### **Room Details Modal**
```jsx
const RoomDetailsModal = ({ roomId }) => {
  // Show detailed room information:
  // - Room basic info
  // - Complete list of assigned students
  // - Capacity utilization chart
  // - Student search/filter functionality
  // - Export student list option
}
```

### **2. Real-time Validation Interface** ⭐ **PRIORITY**

#### **Face Recognition Validator**
```jsx
const FaceRecognitionValidator = () => {
  // Components needed:
  // 1. Room selector dropdown
  // 2. Camera feed component
  // 3. Capture button
  // 4. Validation result display
  // 5. Audio feedback system
  
  const validateStudent = async (imageData, roomCode) => {
    const response = await fetch('/exam-room/recognize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        face_image: imageData,
        room_code: roomCode
      })
    });
    
    const result = await response.json();
    const validation = result.data[0];
    
    // Handle audio feedback
    if (validation.beep_type === 'confirmation') {
      playSuccessBeep(); // Green screen, success sound
      showSuccess(validation.message);
    } else {
      playWarningBeep(); // Red screen, warning sound  
      showError(validation.message);
    }
    
    return validation;
  };
}
```

#### **Validation Result Display**
```jsx
const ValidationResultDisplay = ({ result }) => {
  // Show:
  // - Student photo (if available)
  // - Student name and index number
  // - Room assignment status
  // - Validation message
  // - Timestamp
  // - Color coding (green/red background)
}
```

### **3. Quick Index Lookup Tool**
```jsx
const QuickIndexValidator = () => {
  // Simple form:
  // - Index number input
  // - Room code input  
  // - Validate button
  // - Result display (valid/invalid)
  
  // Use: GET /exam-room/validate/{room_code}/{index_number}
}
```

---

## 📱 **Page Structure & Navigation**

### **Admin Dashboard Layout**
```
/admin/exam-rooms
├── Room Management Tab
│   ├── Create New Room (Form)
│   ├── Room List (Table)
│   └── Room Details (Modal)
├── Validation Center Tab
│   ├── Face Recognition Interface
│   ├── Quick Index Lookup
│   └── Recent Validations Log
└── Analytics Tab
    ├── Room Utilization Charts
    ├── Validation Statistics
    └── System Health
```

### **Exam Monitor Interface** (Can be separate page)
```
/exam-monitor
├── Room Selector
├── Live Camera Feed
├── Validation Results
└── Student Status Board
```

---

## 🎯 **Key User Flows**

### **Admin Room Assignment Flow**
1. **Preview Assignment**
   ```
   Admin enters: index_start=8551521, index_end=8552721
   System shows: "45 students will be assigned to this room"
   Preview shows: First 10 students with names/index numbers
   ```

2. **Create Room**
   ```
   Admin fills form: room_code="FF1", capacity=50
   Admin clicks "Create Room"
   Confirmation: "Assign 45 students to FF1?"
   Success: "Room FF1 created with 45 students assigned!"
   ```

3. **Monitor Rooms**
   ```
   Dashboard shows: FF1 (45/50 students) - 90% utilization
   Admin clicks "View Students" → See complete student list
   ```

### **Real-time Validation Flow**
1. **Setup**
   ```
   Exam proctor selects room: "FF1 - Engineering Hall 1"
   Camera feed activates
   ```

2. **Student Validation**
   ```
   Student enters room → Face captured
   System validates: Index 8551650 in range 8551521-8552721? ✅
   Result: Green screen + "✅ John Doe verified" + success beep
   ```

3. **Invalid Student**
   ```
   Wrong student enters → Face captured  
   System validates: Index 8559999 in range 8551521-8552721? ❌
   Result: Red screen + "⚠️ Student not assigned to this room" + warning beep
   ```

---

## 🔊 **Audio Feedback Implementation**

```javascript
// Audio feedback system
const AudioFeedback = {
  success: new Audio('/sounds/success-beep.mp3'),
  warning: new Audio('/sounds/warning-beep.mp3'),
  
  playSuccess() {
    this.success.currentTime = 0;
    this.success.play().catch(console.error);
  },
  
  playWarning() {
    this.warning.currentTime = 0; 
    this.warning.play().catch(console.error);
  }
};

// Usage in validation
const handleValidation = (result) => {
  if (result.beep_type === 'confirmation') {
    AudioFeedback.playSuccess();
    setScreenColor('green');
    setMessage('✅ ' + result.message);
  } else {
    AudioFeedback.playWarning();
    setScreenColor('red');
    setMessage('⚠️ ' + result.message);
  }
  
  // Auto-clear after 3 seconds
  setTimeout(() => {
    setScreenColor('default');
    setMessage('');
  }, 3000);
};
```

---

## 📊 **Sample API Responses**

### **Room List Response**
```json
{
  "data": [
    {
      "id": "uuid1",
      "room_code": "FF1",
      "room_name": "Engineering Hall 1",
      "index_start": "8551521",
      "index_end": "8552721", 
      "capacity": 50,
      "assigned_students_count": 45,
      "created_at": "2025-08-03T12:00:00Z"
    }
  ]
}
```

### **Validation Response**
```json
{
  "data": [{
    "status": "valid",
    "beep_type": "confirmation",
    "student_name": "John Doe",
    "index_number": "8551650", 
    "room_code": "FF1",
    "room_name": "Engineering Hall 1",
    "message": "✅ John Doe (8551650) verified in FF1 - Range: 8551521-8552721",
    "timestamp": "2025-08-03T12:30:00Z"
  }]
}
```

### **Preview Response**
```json
{
  "data": [{
    "index_start": "8551521",
    "index_end": "8552721",
    "total_students": 45,
    "students_preview": [
      {
        "name": "John Doe",
        "index_number": "8551525",
        "email": "john@knust.edu.gh",
        "college": "College of Engineering"
      }
    ],
    "has_more": true
  }]
}
```

---

## 🎨 **UI/UX Guidelines**

### **Color Scheme**
- **Success**: Green (#22c55e) - Valid student validation
- **Warning**: Red (#ef4444) - Invalid student/errors  
- **Info**: Blue (#3b82f6) - General information
- **Neutral**: Gray (#6b7280) - Default states

### **Typography**
- **Headers**: Bold, clear room names and codes
- **Student Info**: Medium weight for names, light for details
- **Status Messages**: Bold, large text for validation results

### **Layout**
- **Full-screen validation**: Large, clear results during exams
- **Responsive design**: Works on tablets for exam monitoring
- **Quick actions**: Easy access to common functions
- **Real-time updates**: Live data refresh without page reload

### **Accessibility**
- **High contrast**: Clear visibility in exam hall lighting
- **Large buttons**: Easy interaction with gloves/stress
- **Screen readers**: Proper ARIA labels
- **Keyboard navigation**: Full functionality without mouse

---

## 🚀 **Implementation Priority**

### **Phase 1: Core Admin Functions** (Week 1)
1. ✅ Room assignment form with preview
2. ✅ Room management table
3. ✅ Basic CRUD operations
4. ✅ Student count display

### **Phase 2: Real-time Validation** (Week 2) ⭐ **CRITICAL**
1. ✅ Camera integration
2. ✅ Face recognition interface  
3. ✅ Audio feedback system
4. ✅ Validation result display

### **Phase 3: Enhanced Features** (Week 3)
1. ✅ Room details with student lists
2. ✅ Quick index lookup
3. ✅ Analytics and reporting
4. ✅ Export functionality

### **Phase 4: Polish & Testing** (Week 4)
1. ✅ Responsive design
2. ✅ Error handling
3. ✅ Performance optimization
4. ✅ User acceptance testing

---

## 📝 **Technical Requirements**

### **Dependencies Needed**
```bash
# Camera access
npm install react-webcam

# Charts for analytics  
npm install recharts

# Audio handling
npm install howler

# File export
npm install react-csv

# Date handling
npm install date-fns
```

### **Camera Integration**
```jsx
import Webcam from 'react-webcam';

const CameraCapture = ({ onCapture }) => {
  const webcamRef = useRef(null);
  
  const capture = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot();
    onCapture(imageSrc);
  }, [webcamRef, onCapture]);
  
  return (
    <div className="camera-container">
      <Webcam
        ref={webcamRef}
        audio={false}
        screenshotFormat="image/jpeg"
        width={640}
        height={480}
      />
      <button onClick={capture}>Capture & Validate</button>
    </div>
  );
};
```

---

## 🎯 **Success Criteria**

By the end of implementation, the system should:

1. ✅ **Admin can create rooms** and see exact student counts
2. ✅ **Preview functionality** shows students before assignment  
3. ✅ **Real-time validation** works with camera and audio feedback
4. ✅ **Student validation** is instant and accurate
5. ✅ **Audio feedback** provides clear success/error signals
6. ✅ **Room monitoring** shows live utilization data
7. ✅ **Responsive design** works on desktop and tablets
8. ✅ **Error handling** gracefully manages network/camera issues

---

## 📞 **Support & Testing**

### **Testing Checklist**
- [ ] Create room with index range 8551521-8552721
- [ ] Verify 45 students are assigned (example)
- [ ] Test face recognition with valid student in correct room
- [ ] Test face recognition with student in wrong room  
- [ ] Verify success beep plays for valid students
- [ ] Verify warning beep plays for invalid students
- [ ] Test room capacity warnings
- [ ] Test room details modal with student list

### **API Testing**
Use the provided Postman collection:
- `KNUST_Exam_Room_Management.postman_collection.json`
- `KNUST_Exam_Room_Management.postman_environment.json`

### **Contact**
- **Backend API**: All endpoints are ready and documented
- **Database**: Migration scripts provided
- **Testing**: Comprehensive test suite available

---

## 🎉 **Final Goal**

Create an intuitive, reliable exam room management system where:

1. **Admins** can easily assign students to rooms based on index ranges
2. **Exam proctors** can quickly validate students with visual and audio feedback  
3. **Students** get immediate confirmation they're in the correct room
4. **System** handles high-volume, real-time validations during exam periods

**Focus on the real-time validation interface** - this is the most critical component that will be used during actual exams! 🎯
