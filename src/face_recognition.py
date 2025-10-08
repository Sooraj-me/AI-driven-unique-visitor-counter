import cv2
from ultralytics import YOLO
from deepface import DeepFace
import numpy as np

# src/face_recognition.py

class FaceRecognizer:
    def __init__(self):
        # Initialize your model or variables here
        pass

    def recognize(self, face_image):
        # Implement recognition logic here
        # For now, just return a dummy value
        return "unknown"

# Load YOLOv8 model (replace with 'yolov8n-face.pt' if you have a face-specific model)
model = YOLO('yolov8n.pt')

# Open video file or webcam
cap = cv2.VideoCapture(0)  # Change to 0 for webcam
  # Change to 0 for webcam

known_embeddings = []
unique_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 inference on the frame
    results = model(frame)

    # Draw bounding boxes
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                # Optionally, filter by class or confidence
                if conf > 0.3:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Crop the face from the frame
                face_img = frame[y1:y2, x1:x2]

                # Get embedding
                embedding = DeepFace.represent(face_img, model_name="Facenet")[0]["embedding"]

                # Compare with known embeddings
                is_new = True
                for known in known_embeddings:
                    dist = np.linalg.norm(np.array(embedding) - np.array(known))
                    if dist < 10:  # Threshold, tune as needed
                        is_new = False
                        break

                if is_new:
                    known_embeddings.append(embedding)
                    unique_count += 1

    print("Unique visitors:", unique_count)

    cv2.imshow('YOLOv8 Face Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() 