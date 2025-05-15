#!/usr/bin/env python3
"""
Run the Unity client simulator.
"""

import argparse
import asyncio
import logging
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vtuber_backend.core.unity_client import UnityClientSimulator
from vtuber_backend.utils.logging import setup_logging

logger = logging.getLogger(__name__)


async def run_client(url: str):
    """
    Run the Unity client simulator.

    Args:
        url: WebSocket URL of the backend
    """
    simulator = UnityClientSimulator(websocket_url=url)
    await simulator.run()


def main():
    """Run the Unity client simulator."""
    # Configure logging
    setup_logging()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the Unity client simulator")
    parser.add_argument(
        "--url",
        type=str,
        default="ws://localhost:8000/ws",
        help="WebSocket URL of the backend",
    )
    args = parser.parse_args()

    # Run the client
    logger.info(f"Starting client connecting to {args.url}")
    asyncio.run(run_client(args.url))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
