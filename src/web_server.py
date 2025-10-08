#!/usr/bin/env python3
"""
Web server for Face Tracker Dashboard
Run this script to start the web interface independently
"""

import argparse
import json
import os
import sys
from loguru import logger
from .web_interface import run_web_interface
from .logger import setup_logger

def main():
    """
    Main entry point for web server
    """
    parser = argparse.ArgumentParser(description='Face Tracker Web Server')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', default=5000, type=int, help='Port number')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        # Setup logging
        setup_logger(config['log_dir'], args.log_level)
        
        logger.info(f"Starting web server on {args.host}:{args.port}")
        logger.info(f"Dashboard will be available at: http://{args.host}:{args.port}")
        
        # Run web interface
        run_web_interface(config, host=args.host, port=args.port, debug=args.debug)
        
    except KeyboardInterrupt:
        logger.info("Web server stopped by user")
    except Exception as e:
        logger.error(f"Web server failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 