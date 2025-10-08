from flask import Flask, render_template, jsonify, request
import os
import json
from datetime import datetime
from .database import Database
from .utils import get_date_folder

app = Flask(__name__)

class WebInterface:
    def __init__(self, config):
        """
        Initialize web interface
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.database = Database(config['database_path'])
        
    def get_statistics(self):
        """
        Get current statistics
        """
        return self.database.get_visitor_stats()
    
    def get_recent_events(self, limit=20):
        """
        Get recent events
        """
        return self.database.get_recent_events(limit)
    
    def get_visitor_events(self, face_id):
        """
        Get events for specific visitor
        """
        return self.database.get_visitor_events(face_id)

# Global web interface instance
web_interface = None

@app.route('/')
def index():
    """
    Main dashboard page
    """
    if web_interface is None:
        return "Web interface not initialized", 500
    
    stats = web_interface.get_statistics()
    recent_events = web_interface.get_recent_events(10)
    
    return render_template('dashboard.html', stats=stats, events=recent_events)

@app.route('/api/stats')
def api_stats():
    """
    API endpoint for statistics
    """
    if web_interface is None:
        return jsonify({"error": "Web interface not initialized"}), 500
    
    stats = web_interface.get_statistics()
    return jsonify(stats)

@app.route('/api/events')
def api_events():
    """
    API endpoint for recent events
    """
    if web_interface is None:
        return jsonify({"error": "Web interface not initialized"}), 500
    
    limit = request.args.get('limit', 20, type=int)
    events = web_interface.get_recent_events(limit)
    
    # Convert events to serializable format
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'face_id': event.face_id,
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat(),
            'image_path': event.image_path,
            'confidence': event.confidence
        })
    
    return jsonify(event_list)

@app.route('/api/visitor/<face_id>')
def api_visitor(face_id):
    """
    API endpoint for specific visitor events
    """
    if web_interface is None:
        return jsonify({"error": "Web interface not initialized"}), 500
    
    events = web_interface.get_visitor_events(face_id)
    
    # Convert events to serializable format
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'face_id': event.face_id,
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat(),
            'image_path': event.image_path,
            'confidence': event.confidence
        })
    
    return jsonify(event_list)

def create_web_interface(config):
    """
    Create and initialize web interface
    Args:
        config: Configuration dictionary
    """
    global web_interface
    web_interface = WebInterface(config)
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create basic HTML template
    create_html_template(templates_dir)
    
    return app

def create_html_template(templates_dir):
    """
    Create basic HTML template for dashboard
    """
    template_path = os.path.join(templates_dir, 'dashboard.html')
    
    if not os.path.exists(template_path):
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Tracker Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .events-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .event-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .event-item:last-child {
            border-bottom: none;
        }
        .event-type {
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .event-entry {
            background-color: #d4edda;
            color: #155724;
        }
        .event-exit {
            background-color: #f8d7da;
            color: #721c24;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Intelligent Face Tracker Dashboard</h1>
            <p>Real-time visitor tracking and analytics</p>
        </div>
        
        <button class="refresh-btn" onclick="refreshData()">Refresh Data</button>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="total-visitors">-</div>
                <div class="stat-label">Total Visitors</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-events">-</div>
                <div class="stat-label">Total Events</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="entry-events">-</div>
                <div class="stat-label">Entry Events</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="exit-events">-</div>
                <div class="stat-label">Exit Events</div>
            </div>
        </div>
        
        <div class="events-section">
            <h2>Recent Events</h2>
            <div id="events-list">
                <p>Loading events...</p>
            </div>
        </div>
    </div>

    <script>
        function refreshData() {
            // Refresh statistics
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-visitors').textContent = data.total_visitors || 0;
                    document.getElementById('total-events').textContent = data.total_events || 0;
                    document.getElementById('entry-events').textContent = data.entry_events || 0;
                    document.getElementById('exit-events').textContent = data.exit_events || 0;
                })
                .catch(error => console.error('Error fetching stats:', error));
            
            // Refresh events
            fetch('/api/events?limit=10')
                .then(response => response.json())
                .then(data => {
                    const eventsList = document.getElementById('events-list');
                    if (data.length === 0) {
                        eventsList.innerHTML = '<p>No events found</p>';
                        return;
                    }
                    
                    eventsList.innerHTML = data.map(event => `
                        <div class="event-item">
                            <div>
                                <strong>Face ID:</strong> ${event.face_id.substring(0, 8)}...
                                <br>
                                <small>${new Date(event.timestamp).toLocaleString()}</small>
                            </div>
                            <span class="event-type event-${event.event_type}">${event.event_type.toUpperCase()}</span>
                        </div>
                    `).join('');
                })
                .catch(error => console.error('Error fetching events:', error));
        }
        
        // Load data on page load
        document.addEventListener('DOMContentLoaded', refreshData);
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
        """
        
        with open(template_path, 'w') as f:
            f.write(html_content)

def run_web_interface(config, host='0.0.0.0', port=5000, debug=False):
    """
    Run the web interface
    Args:
        config: Configuration dictionary
        host: Host address
        port: Port number
        debug: Debug mode
    """
    app = create_web_interface(config)
    app.run(host=host, port=port, debug=debug) 