#!/usr/bin/env python3
"""
Demo script for Intelligent Face Tracker
This script demonstrates the system functionality with sample data
"""

import os
import sys
import json
import time
import cv2
import numpy as np
from loguru import logger
from src.face_pipeline import FacePipeline
from src.logger import setup_logger
from src.utils import create_directories

def create_sample_video(output_path="data/sample_demo.mp4", duration=10, fps=30):
    """
    Create a sample video for demonstration
    """
    try:
        # Create a simple video with moving rectangles to simulate faces
        width, height = 640, 480
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        logger.info(f"Creating sample video: {output_path}")
        
        for frame_num in range(duration * fps):
            # Create frame
            frame = np.ones((height, width, 3), dtype=np.uint8) * 128
            
            # Add moving rectangles to simulate faces
            t = frame_num / fps
            
            # Face 1 - moving from left to right
            x1 = int(50 + 200 * np.sin(t))
            y1 = 100
            cv2.rectangle(frame, (x1, y1), (x1 + 80, y1 + 80), (0, 255, 0), -1)
            cv2.putText(frame, "Face 1", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Face 2 - moving from top to bottom
            x2 = 300
            y2 = int(50 + 150 * np.cos(t * 0.5))
            cv2.rectangle(frame, (x2, y2), (x2 + 80, y2 + 80), (255, 0, 0), -1)
            cv2.putText(frame, "Face 2", (x2, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Face 3 - appears later
            if frame_num > fps * 5:
                x3 = int(400 + 100 * np.sin(t * 2))
                y3 = 300
                cv2.rectangle(frame, (x3, y3), (x3 + 80, y3 + 80), (0, 0, 255), -1)
                cv2.putText(frame, "Face 3", (x3, y3 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Add timestamp
            cv2.putText(frame, f"Time: {t:.1f}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            out.write(frame)
        
        out.release()
        logger.info("Sample video created successfully")
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating sample video: {e}")
        return None

def run_demo():
    """
    Run the complete demo
    """
    try:
        # Load configuration
        config = {
            "detection_skip_frames": 3,
            "database_path": "database/demo.db",
            "log_dir": "logs/",
            "video_source": "data/sample_demo.mp4"
        }
        
        # Create necessary directories
        create_directories("logs/")
        os.makedirs("data", exist_ok=True)
        os.makedirs("database", exist_ok=True)
        
        # Setup logging
        setup_logger(config['log_dir'], "INFO")
        
        logger.info("Starting Intelligent Face Tracker Demo")
        
        # Create sample video if it doesn't exist
        if not os.path.exists(config['video_source']):
            logger.info("Sample video not found, creating one...")
            video_path = create_sample_video()
            if not video_path:
                logger.error("Failed to create sample video")
                return
        else:
            video_path = config['video_source']
        
        # Initialize face pipeline
        logger.info("Initializing face tracking pipeline...")
        pipeline = FacePipeline(config)
        
        # Process video
        logger.info(f"Processing video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error("Failed to open video")
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video: {total_frames} frames at {fps} FPS")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process frame
            processed_frame = pipeline.process_frame(frame)
            
            # Display frame
            cv2.imshow('Face Tracker Demo', processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(30) & 0xFF  # 30ms delay for ~30 FPS display
            if key == ord('q'):
                logger.info("Demo stopped by user")
                break
            elif key == ord('s'):
                # Save snapshot
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                cv2.imwrite(f"demo_snapshot_{timestamp}.jpg", processed_frame)
                logger.info(f"Snapshot saved: demo_snapshot_{timestamp}.jpg")
            
            # Show progress
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                progress = (frame_count / total_frames) * 100
                logger.info(f"Progress: {progress:.1f}% ({frame_count}/{total_frames}) - FPS: {frame_count/elapsed:.1f}")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Final statistics
        total_time = time.time() - start_time
        stats = pipeline.get_statistics()
        
        logger.info("Demo completed!")
        logger.info(f"Processing time: {total_time:.2f} seconds")
        logger.info(f"Average FPS: {frame_count/total_time:.2f}")
        logger.info(f"Final statistics: {stats}")
        
        # Cleanup
        pipeline.cleanup()
        
        logger.info("Demo files created:")
        logger.info(f"  - Database: {config['database_path']}")
        logger.info(f"  - Logs: {config['log_dir']}")
        logger.info(f"  - Sample video: {video_path}")
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise

def run_web_demo():
    """
    Run web interface demo
    """
    try:
        from src.web_server import main as web_main
        
        logger.info("Starting web interface demo...")
        logger.info("Web dashboard will be available at: http://localhost:5000")
        logger.info("Press Ctrl+C to stop")
        
        # Override sys.argv for web server
        sys.argv = ['web_server', '--port', '5000', '--debug']
        web_main()
        
    except ImportError:
        logger.error("Flask not installed. Install with: pip install Flask")
    except Exception as e:
        logger.error(f"Web demo failed: {e}")

def main():
    """
    Main demo entry point
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Intelligent Face Tracker Demo')
    parser.add_argument('--mode', choices=['video', 'web', 'both'], default='video',
                       help='Demo mode: video processing, web interface, or both')
    parser.add_argument('--no-display', action='store_true', help='Disable video display')
    
    args = parser.parse_args()
    
    if args.mode in ['video', 'both']:
        run_demo()
    
    if args.mode in ['web', 'both']:
        run_web_demo()

if __name__ == '__main__':
    main() 