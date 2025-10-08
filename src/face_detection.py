import cv2
from loguru import logger

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

class FaceDetector:
    def __init__(self, model_path=None):
        """
        Initialize YOLOv5-face or OpenCV Haar Cascade face detector
        """
        self.use_yolo = False
        if model_path and YOLO_AVAILABLE:
            try:
                self.model = YOLO(model_path)
                self.use_yolo = True
                logger.info(f"YOLO model loaded: {model_path}")
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                self.use_yolo = False

        if not self.use_yolo:
            try:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                if self.face_cascade.empty():
                    raise Exception('Failed to load Haar Cascade XML')
                logger.info("OpenCV Haar Cascade face detector initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize face detector: {e}")
                raise

    def detect_faces(self, frame):
        """
        Detect faces in the given frame using YOLO or Haar Cascade
        Returns: List of face bounding boxes [(x1, y1, x2, y2, confidence), ...]
        """
        try:
            if self.use_yolo:
                results = self.model(frame, verbose=False)
                faces = []
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            confidence = box.conf[0].cpu().numpy()
                            if confidence > 0.3:  # Lowered threshold for more sensitivity
                                faces.append((int(x1), int(y1), int(x2), int(y2), float(confidence)))
                return faces
            else:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20))
                results = []
                for (x, y, w, h) in faces:
                    results.append((int(x), int(y), int(x + w), int(y + h), 1.0))
                return results
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return []

    def crop_face(self, frame, bbox):
        x1, y1, x2, y2 = bbox[:4]
        return frame[y1:y2, x1:x2] 