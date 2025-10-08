Intelligent Face Tracker with Auto-Registration & Visitor Counting
🚀 Overview

Intelligent Face Tracker is an AI-powered system that detects, tracks, and recognizes human faces in real time from a video or RTSP stream. It automatically registers new visitors, keeps track of returning ones, and logs all entries and exits with timestamps and face snapshots.

The project is designed for automated visitor management, analytics, and security monitoring — built for real-time performance using cutting-edge computer vision and deep learning models.

✨ Key Features

🔍 Real-Time Face Detection – YOLOv8 for accurate and fast detection

🧩 Face Recognition – InsightFace/ArcFace for robust identity embeddings

🎯 Multi-Object Tracking – OpenCV-based CSRT/KCF tracking

🪪 Auto-Registration – Automatically registers unseen faces with unique IDs

🧾 Structured Logging – Saves entries/exits to filesystem and SQLite database

👥 Unique Visitor Counting – Accurate real-time count of distinct visitors

📊 Web Dashboard – Live statistics, logs, and visitor analytics via Flask

📹 RTSP Support – Works with both video files and live camera feeds

🧱 System Architecture
┌─────────────────┐    ┌────────────────────┐    ┌───────────────────┐
│   Video Input   │───▶│  Face Pipeline     │───▶│   Web Dashboard   │
│ (File/RTSP)     │    │ (Detection, Track) │    │ (Flask + Charts)  │
└─────────────────┘    └────────────────────┘    └───────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌────────────────────┐    ┌─────────────────┐
│   Database      │◀───│   Logging System   │───▶│  Face Snapshots │
│  (SQLite)       │    │   (Events, Errors) │    │ (Date Folders)  │
└─────────────────┘    └────────────────────┘    └─────────────────┘


Face Pipeline Components

FaceDetector → YOLOv8

FaceRecognizer → InsightFace

FaceTracker → OpenCV (CSRT/KCF)

Database → SQLAlchemy ORM

⚙️ Setup Instructions
1. Prerequisites

Python ≥ 3.8

OpenCV (with CUDA recommended for GPU acceleration)

Adequate disk space for logs and database

2. Installation
git clone <your-repo-url>
cd intelligent-face-tracker

pip install -r requirements.txt

3. Configuration

Edit config.json:

{
  "detection_skip_frames": 5,
  "database_path": "database/visitors.db",
  "log_dir": "logs/",
  "video_source": "data/sample_video.mp4"
}

▶️ Usage
Basic Commands
# Process a video
python -m src.main --video data/sample_video.mp4

# Process RTSP stream
python -m src.main --rtsp rtsp://your-camera-url

# Headless (no display)
python -m src.main --video data/sample_video.mp4 --no-display

# Save output video
python -m src.main --video data/sample_video.mp4 --output output.mp4

Web Dashboard
python -m src.web_server --port 5000


Access via 👉 http://localhost:5000

🧩 Project Structure
intelligent-face-tracker/
├── src/
│   ├── main.py              # Entry point
│   ├── face_pipeline.py     # Main face processing pipeline
│   ├── face_detection.py    # YOLOv8 detection
│   ├── face_recognition.py  # InsightFace recognition
│   ├── tracker.py           # OpenCV tracking
│   ├── database.py          # SQLAlchemy ORM
│   ├── logger.py            # Logging setup
│   ├── utils.py             # Helper functions
│   ├── web_interface.py     # Flask web routes
│   └── web_server.py        # Web server entry
├── database/
├── logs/
│   ├── events.log
│   ├── errors.log
│   └── entries/YYYY-MM-DD/
├── data/
├── config.json
├── requirements.txt
└── README.md

⚙️ Configuration Options
Category	Key	Description
Detection	detection_skip_frames	Frames skipped between detections
Detection	confidence_threshold	Minimum YOLO confidence
Database	database_path	SQLite DB path
Logging	log_dir	Directory for logs
Logging	log_level	DEBUG, INFO, WARNING, ERROR
Video	video_source	Path or RTSP URL
Video	output_path	Save processed video
🧾 Database & Logging

Database Tables

Table	Description
visitors	Stores unique visitor data (face_id, first_seen, last_seen, total_visits)
events	Logs entry/exit events with image path and timestamp

Log Files

logs/
├── events.log     # System events
├── errors.log     # Error logs
└── entries/YYYY-MM-DD/   # Cropped face images

📈 Web Dashboard Features

Real-time visitor statistics

Event timeline with thumbnails

Daily visitor trends

Auto-refresh every 30 seconds

⚡ Performance Tips
Goal	Recommendation
Faster Processing	Use CUDA-enabled OpenCV
Faster Inference	Use YOLOv8n model
Save Memory	Skip more frames (detection_skip_frames ↑)
Better Accuracy	Use high-res inputs, YOLOv8l/x
🧰 Troubleshooting
Issue	Solution
CUDA error	Install CPU-only version of OpenCV
Memory overload	Lower resolution or skip frames
DB lock	Stop concurrent DB access
Model load error	Ensure internet for first model download

Debug mode:

python -m src.main --video data/sample_video.mp4 --log-level DEBUG

🌐 API Endpoints
Endpoint	Description
GET /api/stats	Get current system stats
GET /api/events?limit=20	Get recent events
GET /api/visitor/<face_id>	Get visitor history
🤝 Contributing

Fork the repository

Create a new feature branch

Commit and push changes

Open a pull request

📜 License

This project is licensed under the MIT License.

🙏 Acknowledgments

Ultralytics YOLOv8 – Face Detection

InsightFace / ArcFace – Face Recognition

OpenCV – Tracking

Flask – Web Dashboard

🏆 Developed for the Hackathon organized by Katomaran Technologies
