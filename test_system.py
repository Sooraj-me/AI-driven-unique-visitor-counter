#!/usr/bin/env python3
"""
Simple test script to verify system components work
"""

import os
import json
import cv2
import numpy as np
from loguru import logger

def test_basic_components():
    """Test basic system components"""
    print("🧪 Testing Basic System Components...")
    
    # Test 1: Configuration loading
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✅ Configuration loading: PASSED")
    except Exception as e:
        print(f"❌ Configuration loading: FAILED - {e}")
        return False
    
    # Test 2: Directory creation
    try:
        os.makedirs('logs', exist_ok=True)
        os.makedirs('database', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        print("✅ Directory creation: PASSED")
    except Exception as e:
        print(f"❌ Directory creation: FAILED - {e}")
        return False
    
    # Test 3: OpenCV functionality
    try:
        # Create a test image
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        cv2.rectangle(test_image, (100, 100), (200, 200), (0, 255, 0), 2)
        cv2.imwrite('test_image.jpg', test_image)
        print("✅ OpenCV functionality: PASSED")
    except Exception as e:
        print(f"❌ OpenCV functionality: FAILED - {e}")
        return False
    
    # Test 4: Database connection (without models)
    try:
        from src.database import Database
        db = Database('database/test.db')
        print("✅ Database connection: PASSED")
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False
    
    # Test 5: Logging system
    try:
        from src.logger import setup_logger
        logger = setup_logger('logs', 'INFO')
        logger.info("Test log message")
        print("✅ Logging system: PASSED")
    except Exception as e:
        print(f"❌ Logging system: FAILED - {e}")
        return False
    
    # Test 6: Utility functions
    try:
        from src.utils import get_timestamp, get_date_folder
        timestamp = get_timestamp()
        date_folder = get_date_folder()
        print(f"✅ Utility functions: PASSED (Timestamp: {timestamp}, Date: {date_folder})")
    except Exception as e:
        print(f"❌ Utility functions: FAILED - {e}")
        return False
    
    print("\n🎉 All basic tests passed!")
    return True

def test_web_interface():
    """Test web interface components"""
    print("\n🌐 Testing Web Interface Components...")
    
    try:
        from src.web_interface import create_web_interface
        config = {'database_path': 'database/test.db', 'log_dir': 'logs/'}
        app = create_web_interface(config)
        print("✅ Web interface creation: PASSED")
    except Exception as e:
        print(f"❌ Web interface creation: FAILED - {e}")
        return False
    
    return True

def create_sample_output():
    """Create sample output files for demonstration"""
    print("\n📁 Creating Sample Output Files...")
    
    try:
        # Create sample log entry
        with open('logs/events.log', 'w') as f:
            f.write("2024-01-01 10:00:00 | INFO | System initialized\n")
            f.write("2024-01-01 10:00:05 | INFO | Face detected: ID-12345\n")
            f.write("2024-01-01 10:00:10 | INFO | Face registered: ID-67890\n")
        
        # Create sample database entries
        from src.database import Database
        db = Database('database/demo.db')
        
        # Add sample visitors
        db.add_visitor("test-face-001")
        db.add_visitor("test-face-002")
        
        # Add sample events
        db.log_event("test-face-001", "entry", "logs/entries/2024-01-01/test_001_entry.jpg")
        db.log_event("test-face-001", "exit", "logs/entries/2024-01-01/test_001_exit.jpg")
        db.log_event("test-face-002", "entry", "logs/entries/2024-01-01/test_002_entry.jpg")
        
        print("✅ Sample output files created")
        
        # Show statistics
        stats = db.get_visitor_stats()
        print(f"📊 Sample Statistics: {stats}")
        
    except Exception as e:
        print(f"❌ Sample output creation: FAILED - {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Intelligent Face Tracker - System Test")
    print("=" * 50)
    
    # Run tests
    basic_ok = test_basic_components()
    web_ok = test_web_interface()
    sample_ok = create_sample_output()
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print(f"Basic Components: {'✅ PASSED' if basic_ok else '❌ FAILED'}")
    print(f"Web Interface: {'✅ PASSED' if web_ok else '❌ FAILED'}")
    print(f"Sample Output: {'✅ PASSED' if sample_ok else '❌ FAILED'}")
    
    if basic_ok and web_ok and sample_ok:
        print("\n🎉 All tests passed! System is ready for hackathon submission.")
        print("\n📝 Next steps:")
        print("1. Download the sample video from the provided Drive link")
        print("2. Place it in the 'data/' folder")
        print("3. Run: python -m src.main --video data/your_video.mp4")
        print("4. Start web dashboard: python -m src.web_server")
        print("5. Create your demonstration video")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == '__main__':
    main() 