#!/usr/bin/env python3
"""
Run the VTuber backend server.
"""

import argparse
import logging
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vtuber_backend.core.app import run_server
from vtuber_backend.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Run the VTuber backend server."""
    # Configure logging
    setup_logging()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the VTuber backend server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    args = parser.parse_args()

    # Run the server
    logger.info(f"Starting server on {args.host}:{args.port}")
    run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
