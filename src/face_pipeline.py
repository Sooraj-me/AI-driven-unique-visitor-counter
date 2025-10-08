import cv2
import numpy as np
import time
from loguru import logger
from .face_detection import FaceDetector
from .face_recognition import FaceRecognizer
from .tracker import FaceTracker
from .database import Database
from .utils import save_cropped_face, draw_bbox, calculate_iou, get_timestamp

class FacePipeline:
    def __init__(self, config):
        """
        Initialize the complete face processing pipeline
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.frame_count = 0
        self.detection_skip_frames = config.get('detection_skip_frames', 5)
        
        # Initialize components
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer()
        self.tracker = FaceTracker()
        self.database = Database(config['database_path'])
        
        # State tracking
        self.current_faces = {}  # {face_id: {'bbox': bbox, 'last_seen': timestamp}}
        self.face_history = {}   # Track face movements for exit detection
        
        logger.info("Face pipeline initialized successfully")

    def process_frame(self, frame):
        """
        Process a single frame through the complete pipeline
        Args:
            frame: Input frame (numpy array)
        Returns:
            Processed frame with annotations
        """
        self.frame_count += 1
        processed_frame = frame.copy()
        
        try:
            # Update trackers
            tracked_faces = self.tracker.update(frame)
            
            # Run detection every N frames
            if self.frame_count % self.detection_skip_frames == 0:
                detected_faces = self.detector.detect_faces(frame)
                self._process_detections(frame, detected_faces, tracked_faces)
            
            # Process tracked faces
            self._process_tracked_faces(frame, tracked_faces)
            
            # Check for face exits
            self._check_face_exits(frame)
            
            # Draw annotations
            processed_frame = self._draw_annotations(processed_frame)
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
        
        return processed_frame

    def _process_detections(self, frame, detected_faces, tracked_faces):
        """
        Process detected faces and match with tracked faces
        """
        for bbox in detected_faces:
            x1, y1, x2, y2, confidence = bbox
            
            # Check if this detection matches any tracked face
            matched_tracker = self._match_detection_to_tracker(bbox, tracked_faces)
            
            if matched_tracker is None:
                # New face detected
                self._process_new_face(frame, bbox, confidence)
            else:
                # Update existing tracker
                self._update_tracker(matched_tracker, bbox)

    def _process_new_face(self, frame, bbox, confidence):
        """
        Process a newly detected face
        """
        try:
            # Crop face for recognition
            face_img = self.detector.crop_face(frame, bbox)
            if face_img is None or face_img.size == 0:
                return
            
            # Generate embedding
            embedding = self.recognizer.get_embedding(face_img)
            if embedding is None:
                return
            
            # Try to recognize face
            face_id = self.recognizer.recognize_face(embedding)
            
            if face_id is None:
                # New face - register it
                face_id = self.recognizer.register_new_face(embedding)
                if not self.database.visitor_exists(face_id):
                    self.database.add_visitor(face_id)
                    logger.info(f"Registered new visitor: {face_id}")
            
            # Add to tracker
            tracker_id = self.tracker.add_face(frame, bbox, face_id)
            if tracker_id is not None:
                # Log entry event
                image_path = save_cropped_face(face_img, self.config['log_dir'], face_id, 'entry')
                self.database.log_event(face_id, 'entry', image_path, confidence)
                
                # Update current faces
                self.current_faces[face_id] = {
                    'bbox': bbox,
                    'last_seen': time.time(),
                    'tracker_id': tracker_id
                }
                
                logger.info(f"New face entered: {face_id}")
            
        except Exception as e:
            logger.error(f"Error processing new face: {e}")

    def _match_detection_to_tracker(self, bbox, tracked_faces):
        """
        Match detection to existing tracker using IoU
        """
        best_iou = 0.5  # IoU threshold
        best_match = None
        
        for tracked in tracked_faces:
            tracked_bbox = tracked['bbox']
            iou = calculate_iou(bbox[:4], tracked_bbox)
            
            if iou > best_iou:
                best_iou = iou
                best_match = tracked
        
        return best_match

    def _update_tracker(self, tracked_face, bbox):
        """
        Update existing tracker with new detection
        """
        face_id = tracked_face['face_id']
        if face_id in self.current_faces:
            self.current_faces[face_id]['bbox'] = bbox
            self.current_faces[face_id]['last_seen'] = time.time()

    def _process_tracked_faces(self, frame, tracked_faces):
        """
        Process currently tracked faces
        """
        current_face_ids = set()
        
        for tracked in tracked_faces:
            face_id = tracked['face_id']
            if face_id:
                current_face_ids.add(face_id)
                
                # Update database
                self.database.update_visitor_last_seen(face_id)
                
                # Update current faces
                if face_id in self.current_faces:
                    self.current_faces[face_id]['bbox'] = tracked['bbox']
                    self.current_faces[face_id]['last_seen'] = time.time()

    def _check_face_exits(self, frame):
        """
        Check for faces that have exited the frame
        """
        current_time = time.time()
        exit_threshold = 2.0  # Seconds without detection
        
        for face_id, face_info in list(self.current_faces.items()):
            if current_time - face_info['last_seen'] > exit_threshold:
                # Face has exited
                self._process_face_exit(frame, face_id, face_info)

    def _process_face_exit(self, frame, face_id, face_info):
        """
        Process face exit event
        """
        try:
            # Crop face for exit logging
            bbox = face_info['bbox']
            face_img = self.detector.crop_face(frame, bbox)
            
            if face_img is not None and face_img.size > 0:
                # Log exit event
                image_path = save_cropped_face(face_img, self.config['log_dir'], face_id, 'exit')
                self.database.log_event(face_id, 'exit', image_path)
                
                logger.info(f"Face exited: {face_id}")
            
            # Remove from current faces
            del self.current_faces[face_id]
            
        except Exception as e:
            logger.error(f"Error processing face exit: {e}")

    def _draw_annotations(self, frame):
        """
        Draw bounding boxes and labels on frame
        """
        # Draw current faces
        for face_id, face_info in self.current_faces.items():
            bbox = face_info['bbox']
            label = f"ID: {face_id[:8]}"
            frame = draw_bbox(frame, bbox, label, color=(0, 255, 0))
        
        # Draw statistics
        visitor_count = self.database.get_unique_visitor_count()
        current_count = len(self.current_faces)
        
        # Add text overlay
        cv2.putText(frame, f"Total Visitors: {visitor_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Current: {current_count}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame

    def get_statistics(self):
        """
        Get current pipeline statistics
        """
        stats = self.database.get_visitor_stats()
        stats['current_faces'] = len(self.current_faces)
        stats['frame_count'] = self.frame_count
        return stats

    def cleanup(self):
        """
        Clean up resources
        """
        try:
            self.database.close()
            logger.info("Face pipeline cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}") 