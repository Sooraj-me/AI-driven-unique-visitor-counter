# Intelligent Face Tracker with Auto-Registration and Visitor Counting

## Overview
This project is an AI-driven unique visitor counter that processes a video stream to detect, track, and recognize faces in real-time. It automatically registers new faces, recognizes them in subsequent frames, and tracks them until they exit the frame. All entries and exits are logged with timestamped images and stored both locally and in a database.

## Features
- **Real-time Face Detection**: Using YOLOv8 for accurate face detection
- **Face Recognition**: State-of-the-art InsightFace/ArcFace embeddings
- **Multi-Object Tracking**: OpenCV-based tracking with CSRT/KCF algorithms
- **Auto-Registration**: New faces automatically registered with unique IDs
- **Structured Logging**: Comprehensive logging to filesystem, database, and log files
- **Unique Visitor Counting**: Accurate count of unique visitors
- **Web Dashboard**: Real-time web interface for monitoring and analytics
- **RTSP Support**: Works with both video files and live RTSP streams

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Video Input   │───▶│  Face Pipeline  │───▶│   Web Dashboard │
│ (File/RTSP)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │◀───│   Logging       │───▶│  Face Images    │
│ (SQLite)        │    │   System        │    │ (Date Folders)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘

Face Pipeline Components:
├── FaceDetector (YOLOv8)
├── FaceRecognizer (InsightFace)
├── FaceTracker (OpenCV)
└── Database (SQLAlchemy)
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- OpenCV with CUDA support (recommended for better performance)
- Sufficient disk space for logs and database

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd intelligent-face-tracker

# Install dependencies
pip install -r requirements.txt

# Download sample video (optional)
# Place your video file in the data/ directory
```

### 3. Configuration
Edit `config.json` to customize settings:
```json
{
  "detection_skip_frames": 5,
  "database_path": "database/visitors.db",
  "log_dir": "logs/",
  "video_source": "data/sample_video.mp4"
}
```

### 4. Usage

#### Basic Usage
```bash
# Process video file
python -m src.main --video data/sample_video.mp4

# Process RTSP stream
python -m src.main --rtsp rtsp://your-camera-url

# Run without display (headless mode)
python -m src.main --video data/sample_video.mp4 --no-display

# Save output video
python -m src.main --video data/sample_video.mp4 --output output.mp4
```

#### Web Dashboard
```bash
# Start web server (in separate terminal)
python -m src.web_server --port 5000

# Access dashboard at http://localhost:5000
```

#### Advanced Options
```bash
# Custom configuration
python -m src.main --config custom_config.json

# Debug mode
python -m src.main --video data/sample_video.mp4 --log-level DEBUG

# Web server with custom settings
python -m src.web_server --host 0.0.0.0 --port 8080 --debug
```

## Project Structure
```
intelligent-face-tracker/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   ├── face_pipeline.py     # Complete face processing pipeline
│   ├── face_detection.py    # YOLOv8 face detection
│   ├── face_recognition.py  # InsightFace recognition
│   ├── tracker.py           # OpenCV tracking
│   ├── database.py          # SQLAlchemy database operations
│   ├── utils.py             # Utility functions
│   ├── logger.py            # Logging configuration
│   ├── web_interface.py     # Flask web interface
│   └── web_server.py        # Web server entry point
├── database/                # SQLite database files
├── logs/                    # Log files and face images
│   ├── events.log          # System events
│   ├── errors.log          # Error logs
│   └── entries/            # Cropped face images
│       └── YYYY-MM-DD/     # Date-based organization
├── data/                   # Video files
├── config.json             # Configuration
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Configuration Options

### Detection Settings
- `detection_skip_frames`: Frames to skip between detections (default: 5)
- `confidence_threshold`: Minimum confidence for face detection (default: 0.5)

### Database Settings
- `database_path`: Path to SQLite database file
- `backup_interval`: Database backup interval in hours

### Logging Settings
- `log_dir`: Directory for log files
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `log_rotation`: Log file rotation size (default: 10 MB)

### Video Settings
- `video_source`: Path to video file or RTSP URL
- `output_path`: Optional output video path
- `fps_limit`: Maximum processing FPS

## Output and Logging

### Database Tables
- **visitors**: Unique visitor information
  - `id`: Primary key
  - `face_id`: Unique face identifier
  - `first_seen`: First detection timestamp
  - `last_seen`: Last detection timestamp
  - `total_visits`: Number of visits

- **events**: Entry/exit events
  - `id`: Primary key
  - `face_id`: Face identifier
  - `event_type`: 'entry' or 'exit'
  - `timestamp`: Event timestamp
  - `image_path`: Path to cropped face image
  - `confidence`: Detection confidence

### Log Files
- `logs/events.log`: All system events
- `logs/errors.log`: Error messages only
- `logs/entries/YYYY-MM-DD/`: Cropped face images organized by date

### Web Dashboard
- Real-time statistics
- Recent events list
- Visitor analytics
- Auto-refresh every 30 seconds

## Performance Optimization

### For Better Performance
1. **GPU Acceleration**: Install CUDA-enabled OpenCV
2. **Model Optimization**: Use smaller YOLO models (yolov8n)
3. **Frame Skipping**: Increase `detection_skip_frames` for faster processing
4. **Database Optimization**: Use SSD storage for database files

### For Better Accuracy
1. **Higher Resolution**: Use higher resolution video sources
2. **Lower Frame Skip**: Decrease `detection_skip_frames`
3. **Model Selection**: Use larger YOLO models (yolov8l, yolov8x)

## Troubleshooting

### Common Issues
1. **CUDA Errors**: Install CPU-only versions if GPU unavailable
2. **Memory Issues**: Reduce video resolution or increase frame skip
3. **Database Lock**: Ensure no other processes are accessing the database
4. **Model Download**: Ensure internet connection for first run

### Debug Mode
```bash
python -m src.main --video data/sample_video.mp4 --log-level DEBUG
```

## API Endpoints

### Web Interface API
- `GET /api/stats`: Get current statistics
- `GET /api/events?limit=20`: Get recent events
- `GET /api/visitor/<face_id>`: Get events for specific visitor

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License
This project is licensed under the MIT License.

## Acknowledgments
- YOLOv8 by Ultralytics
- InsightFace by DeepInsight
- OpenCV community
- Flask web framework

---
This project is a part of a hackathon run by https://katomaran.com 