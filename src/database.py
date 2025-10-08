from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from loguru import logger
import os

Base = declarative_base()

class Visitor(Base):
    __tablename__ = 'visitors'
    id = Column(Integer, primary_key=True)
    face_id = Column(String(255), unique=True, nullable=False)
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    total_visits = Column(Integer, default=1)

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    face_id = Column(String(255), nullable=False)
    event_type = Column(String(50), nullable=False)  # 'entry' or 'exit'
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    image_path = Column(Text, nullable=True)
    confidence = Column(String(50), nullable=True)

class Database:
    def __init__(self, db_path):
        """
        Initialize database connection
        Args:
            db_path: Path to SQLite database file
        """
        try:
            # Ensure database directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            self.engine = create_engine(f'sqlite:///{db_path}')
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info(f"Database initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def add_visitor(self, face_id):
        """
        Add a new visitor to the database
        Args:
            face_id: Unique face identifier
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.Session()
            visitor = Visitor(face_id=face_id)
            session.add(visitor)
            session.commit()
            session.close()
            logger.info(f"Added new visitor: {face_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding visitor {face_id}: {e}")
            session.rollback()
            session.close()
            return False

    def update_visitor_last_seen(self, face_id):
        """
        Update visitor's last seen timestamp
        Args:
            face_id: Face identifier
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.Session()
            visitor = session.query(Visitor).filter_by(face_id=face_id).first()
            if visitor:
                visitor.last_seen = datetime.datetime.utcnow()
                visitor.total_visits += 1
                session.commit()
                session.close()
                return True
            else:
                session.close()
                return False
        except Exception as e:
            logger.error(f"Error updating visitor {face_id}: {e}")
            session.rollback()
            session.close()
            return False

    def log_event(self, face_id, event_type, image_path=None, confidence=None):
        """
        Log an event (entry/exit) to the database
        Args:
            face_id: Face identifier
            event_type: 'entry' or 'exit'
            image_path: Path to cropped face image
            confidence: Detection confidence
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.Session()
            event = Event(
                face_id=face_id,
                event_type=event_type,
                image_path=image_path,
                confidence=str(confidence) if confidence else None
            )
            session.add(event)
            session.commit()
            session.close()
            logger.info(f"Logged {event_type} event for face {face_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging event for {face_id}: {e}")
            session.rollback()
            session.close()
            return False

    def get_unique_visitor_count(self):
        """
        Get the total number of unique visitors
        Returns:
            Number of unique visitors
        """
        try:
            session = self.Session()
            count = session.query(Visitor).count()
            session.close()
            return count
        except Exception as e:
            logger.error(f"Error getting visitor count: {e}")
            session.close()
            return 0

    def get_visitor_events(self, face_id):
        """
        Get all events for a specific visitor
        Args:
            face_id: Face identifier
        Returns:
            List of events
        """
        try:
            session = self.Session()
            events = session.query(Event).filter_by(face_id=face_id).order_by(Event.timestamp).all()
            session.close()
            return events
        except Exception as e:
            logger.error(f"Error getting events for {face_id}: {e}")
            session.close()
            return []

    def get_recent_events(self, limit=100):
        """
        Get recent events
        Args:
            limit: Maximum number of events to return
        Returns:
            List of recent events
        """
        try:
            session = self.Session()
            events = session.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()
            session.close()
            return events
        except Exception as e:
            logger.error(f"Error getting recent events: {e}")
            session.close()
            return []

    def visitor_exists(self, face_id):
        """
        Check if a visitor exists in the database
        Args:
            face_id: Face identifier
        Returns:
            True if visitor exists, False otherwise
        """
        try:
            session = self.Session()
            visitor = session.query(Visitor).filter_by(face_id=face_id).first()
            session.close()
            return visitor is not None
        except Exception as e:
            logger.error(f"Error checking visitor existence: {e}")
            session.close()
            return False

    def get_visitor_stats(self):
        """
        Get visitor statistics
        Returns:
            Dictionary with visitor statistics
        """
        try:
            session = self.Session()
            total_visitors = session.query(Visitor).count()
            total_events = session.query(Event).count()
            entry_events = session.query(Event).filter_by(event_type='entry').count()
            exit_events = session.query(Event).filter_by(event_type='exit').count()
            session.close()
            
            return {
                'total_visitors': total_visitors,
                'total_events': total_events,
                'entry_events': entry_events,
                'exit_events': exit_events
            }
        except Exception as e:
            logger.error(f"Error getting visitor stats: {e}")
            session.close()
            return {}

    def close(self):
        """
        Close database connection
        """
        try:
            self.engine.dispose()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}") 