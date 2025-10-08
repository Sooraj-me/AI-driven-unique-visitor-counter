import cv2
import numpy as np
from loguru import logger
from collections import defaultdict

class FaceTracker:
    def __init__(self, tracker_type='CSRT'):
        """
        Initialize face tracker
        Args:
            tracker_type: Type of OpenCV tracker ('CSRT', 'KCF', 'MOSSE', etc.)
        """
        self.trackers = {}
        self.tracker_type = tracker_type
        self.next_tracker_id = 0
        self.tracked_faces = {}  # {tracker_id: face_info}
        self.lost_trackers = defaultdict(int)  # Count frames lost for each tracker
        self.max_lost_frames = 30  # Remove tracker after this many lost frames
        
        logger.info(f"Face tracker initialized with {tracker_type} algorithm")

    def create_tracker(self):
        """
        Create a new tracker instance
        Returns:
            OpenCV tracker instance
        """
        if self.tracker_type == 'CSRT':
            return cv2.TrackerCSRT_create()
        elif self.tracker_type == 'KCF':
            return cv2.TrackerKCF_create()
        elif self.tracker_type == 'MOSSE':
            return cv2.TrackerMOSSE_create()
        else:
            return cv2.TrackerCSRT_create()

    def add_face(self, frame, bbox, face_id=None):
        """
        Add a new face to track
        Args:
            frame: Current frame
            bbox: Bounding box (x1, y1, x2, y2)
            face_id: Optional face ID for recognition
        Returns:
            Tracker ID
        """
        tracker_id = self.next_tracker_id
        self.next_tracker_id += 1
        
        # Create new tracker
        tracker = self.create_tracker()
        x1, y1, x2, y2 = bbox[:4]
        bbox_cv = (x1, y1, x2 - x1, y2 - y1)  # OpenCV format: (x, y, width, height)
        
        success = tracker.init(frame, bbox_cv)
        if success:
            self.trackers[tracker_id] = tracker
            self.tracked_faces[tracker_id] = {
                'face_id': face_id,
                'bbox': bbox,
                'lost_frames': 0
            }
            logger.info(f"Added face {face_id} to tracker {tracker_id}")
            return tracker_id
        else:
            logger.warning(f"Failed to initialize tracker for face {face_id}")
            return None

    def update(self, frame):
        """
        Update all trackers with current frame
        Args:
            frame: Current frame
        Returns:
            List of tracked faces with their bounding boxes and IDs
        """
        active_trackers = []
        
        for tracker_id, tracker in list(self.trackers.items()):
            success, bbox = tracker.update(frame)
            
            if success:
                # Update tracked face info
                x, y, w, h = bbox
                new_bbox = (int(x), int(y), int(x + w), int(y + h))
                self.tracked_faces[tracker_id]['bbox'] = new_bbox
                self.tracked_faces[tracker_id]['lost_frames'] = 0
                
                active_trackers.append({
                    'tracker_id': tracker_id,
                    'face_id': self.tracked_faces[tracker_id]['face_id'],
                    'bbox': new_bbox
                })
            else:
                # Increment lost frames counter
                self.tracked_faces[tracker_id]['lost_frames'] += 1
                self.lost_trackers[tracker_id] += 1
                
                # Remove tracker if lost for too many frames
                if self.lost_trackers[tracker_id] > self.max_lost_frames:
                    self.remove_tracker(tracker_id)
                    logger.info(f"Removed lost tracker {tracker_id}")
        
        return active_trackers

    def remove_tracker(self, tracker_id):
        """
        Remove a tracker
        Args:
            tracker_id: ID of tracker to remove
        """
        if tracker_id in self.trackers:
            del self.trackers[tracker_id]
        if tracker_id in self.tracked_faces:
            del self.tracked_faces[tracker_id]
        if tracker_id in self.lost_trackers:
            del self.lost_trackers[tracker_id]

    def get_tracked_face_ids(self):
        """
        Get list of currently tracked face IDs
        Returns:
            List of face IDs
        """
        return [info['face_id'] for info in self.tracked_faces.values() if info['face_id'] is not None]

    def update_face_id(self, tracker_id, face_id):
        """
        Update face ID for a tracker
        Args:
            tracker_id: Tracker ID
            face_id: New face ID
        """
        if tracker_id in self.tracked_faces:
            self.tracked_faces[tracker_id]['face_id'] = face_id

    def clear(self):
        """
        Clear all trackers
        """
        self.trackers.clear()
        self.tracked_faces.clear()
        self.lost_trackers.clear()
        self.next_tracker_id = 0
        logger.info("All trackers cleared") 