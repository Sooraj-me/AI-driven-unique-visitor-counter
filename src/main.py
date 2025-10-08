import os
import json
import cv2
import time
import argparse
from loguru import logger
from .face_pipeline import FacePipeline
from .utils import create_directories, format_time_duration

def load_config(config_path='config.json'):
    """
    Load configuration from JSON file
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise

def process_video(video_source, pipeline, output_path=None, show_display=True):
    """
    Process video file, webcam, or stream
    Args:
        video_source: Path to video file, RTSP URL, or integer for webcam
        pipeline: FacePipeline instance
        output_path: Optional output video path
        show_display: Whether to show live display
    """
    try:
        # Open video capture
        if isinstance(video_source, int):
            cap = cv2.VideoCapture(video_source)
            logger.info(f"Using webcam (device {video_source}) as video source.")
        else:
            cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            logger.error(f"Failed to open video source: {video_source}")
            return
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.info(f"Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
        
        # Setup video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            logger.info(f"Output video will be saved to: {output_path}")
        
        # Process frames
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("End of video stream or cannot read frame.")
                break
            
            frame_count += 1
            
            # Process frame through pipeline
            processed_frame = pipeline.process_frame(frame)
            
            # Write to output video
            if writer:
                writer.write(processed_frame)
            
            # Display frame
            if show_display:
                cv2.imshow('Face Tracker', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("User requested quit")
                    break
                elif key == ord('s'):
                    # Save current frame
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f"snapshot_{timestamp}.jpg", processed_frame)
                    logger.info(f"Snapshot saved: snapshot_{timestamp}.jpg")
            
            # Log progress
            if frame_count % 100 == 0:
                elapsed_time = time.time() - start_time
                fps_actual = frame_count / elapsed_time
                logger.info(f"Processed {frame_count} frames, FPS: {fps_actual:.2f}")
        
        # Cleanup
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        # Final statistics
        total_time = time.time() - start_time
        logger.info(f"Processing completed:")
        logger.info(f"  Total frames: {frame_count}")
        logger.info(f"  Total time: {format_time_duration(total_time)}")
        logger.info(f"  Average FPS: {frame_count/total_time:.2f}")
        
        stats = pipeline.get_statistics()
        logger.info(f"Final statistics: {stats}")
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise

def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description='Intelligent Face Tracker')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--video', help='Video file path (overrides config)')
    parser.add_argument('--rtsp', help='RTSP stream URL (overrides config)')
    parser.add_argument('--output', help='Output video path')
    parser.add_argument('--no-display', action='store_true', help='Disable live display')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), level=args.log_level)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Override video source if provided
        video_source = None
        if args.video:
            video_source = args.video
        elif args.rtsp:
            video_source = args.rtsp
        else:
            video_source = 0  # Use default webcam
            print("No video file provided. Using webcam (device 0). Press 'q' to quit.")
        
        # Create necessary directories
        create_directories(config['log_dir'])
        
        # Initialize face pipeline
        logger.info("Initializing face tracking pipeline...")
        pipeline = FacePipeline(config)
        
        # Process video or webcam
        logger.info(f"Starting video processing: {video_source}")
        process_video(
            video_source=video_source,
            pipeline=pipeline,
            output_path=args.output,
            show_display=not args.no_display
        )
        
        # Cleanup
        pipeline.cleanup()
        logger.info("Processing completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise

if __name__ == '__main__':
    main() 