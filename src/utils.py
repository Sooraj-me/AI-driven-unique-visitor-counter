import os
import cv2
import numpy as np
from datetime import datetime
from PIL import Image
from loguru import logger

def get_timestamp():
    """Get current timestamp in formatted string"""
    return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

def get_date_folder():
    """Get current date folder name"""
    return datetime.now().strftime('%Y-%m-%d')

def save_cropped_face(image, save_dir, face_id, event_type):
    """
    Save cropped face image to structured folder system
    Args:
        image: Face image (numpy array)
        save_dir: Base directory for saving
        face_id: Face identifier
        event_type: 'entry' or 'exit'
    Returns:
        Path to saved image
    """
    try:
        # Create date-based folder structure
        date_folder = get_date_folder()
        full_save_dir = os.path.join(save_dir, 'entries', date_folder)
        os.makedirs(full_save_dir, exist_ok=True)
        
        # Generate filename
        timestamp = get_timestamp()
        filename = f'{face_id}_{event_type}_{timestamp}.jpg'
        path = os.path.join(full_save_dir, filename)
        
        # Convert BGR to RGB if needed and save
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Convert BGR to RGB for PIL
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            Image.fromarray(image_rgb).save(path)
        else:
            Image.fromarray(image).save(path)
        
        logger.info(f"Saved face image: {path}")
        return path
    except Exception as e:
        logger.error(f"Error saving face image: {e}")
        return None

def resize_image(image, max_size=640):
    """
    Resize image while maintaining aspect ratio
    Args:
        image: Input image
        max_size: Maximum dimension size
    Returns:
        Resized image
    """
    try:
        height, width = image.shape[:2]
        if height <= max_size and width <= max_size:
            return image
        
        # Calculate new dimensions
        if height > width:
            new_height = max_size
            new_width = int(width * max_size / height)
        else:
            new_width = max_size
            new_height = int(height * max_size / width)
        
        return cv2.resize(image, (new_width, new_height))
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return image

def draw_bbox(image, bbox, label=None, color=(0, 255, 0), thickness=2):
    """
    Draw bounding box on image
    Args:
        image: Input image
        bbox: Bounding box (x1, y1, x2, y2)
        label: Optional label text
        color: BGR color tuple
        thickness: Line thickness
    Returns:
        Image with drawn bounding box
    """
    try:
        x1, y1, x2, y2 = bbox[:4]
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
        
        if label:
            # Add label background
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(image, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
            
            # Add label text
            cv2.putText(image, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return image
    except Exception as e:
        logger.error(f"Error drawing bounding box: {e}")
        return image

def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union (IoU) between two bounding boxes
    Args:
        box1: First bounding box (x1, y1, x2, y2)
        box2: Second bounding box (x1, y1, x2, y2)
    Returns:
        IoU value (0-1)
    """
    try:
        # Calculate intersection coordinates
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        # Calculate intersection area
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        
        # Calculate union area
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    except Exception as e:
        logger.error(f"Error calculating IoU: {e}")
        return 0

def create_directories(base_path):
    """
    Create necessary directories for the application
    Args:
        base_path: Base path for creating directories
    """
    try:
        directories = [
            os.path.join(base_path, 'entries'),
            os.path.join(base_path, 'database'),
            os.path.join(base_path, 'models')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    except Exception as e:
        logger.error(f"Error creating directories: {e}")

def format_time_duration(seconds):
    """
    Format time duration in human-readable format
    Args:
        seconds: Duration in seconds
    Returns:
        Formatted time string
    """
    try:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    except Exception as e:
        logger.error(f"Error formatting time duration: {e}")
        return "0s" 