#!/usr/bin/env python3
"""
Main entry point for the VTuber backend.
"""

import argparse
import asyncio
import logging
import sys

from vtuber_backend.core.app import run_server
from vtuber_backend.core.unity_client import UnityClientSimulator
from vtuber_backend.tts.mock_server import run_server as run_mock_tts
from vtuber_backend.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the VTuber backend."""
    # Configure logging
    setup_logging()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="VTuber backend")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Server command
    server_parser = subparsers.add_parser("server", help="Run the backend server")
    server_parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to bind to"
    )
    server_parser.add_argument(
        "--port", type=int, default=8000, help="Port to listen on"
    )

    # Client command
    client_parser = subparsers.add_parser(
        "client", help="Run the Unity client simulator"
    )
    client_parser.add_argument(
        "--url",
        type=str,
        default="ws://localhost:8000/ws",
        help="WebSocket URL of the backend",
    )

    # Mock TTS server command
    mock_parser = subparsers.add_parser("mock-tts", help="Run the mock TTS server")
    mock_parser.add_argument(
        "--host", type=str, default="localhost", help="Host to bind to"
    )
    mock_parser.add_argument("--port", type=int, default=8080, help="Port to listen on")

    # Parse arguments
    args = parser.parse_args()

    # Run the appropriate command
    if args.command == "server":
        logger.info(f"Starting server on {args.host}:{args.port}")
        run_server(host=args.host, port=args.port)
    elif args.command == "client":
        logger.info(f"Starting client connecting to {args.url}")
        asyncio.run(run_client(args.url))
    elif args.command == "mock-tts":
        logger.info(f"Starting mock TTS server on {args.host}:{args.port}")
        asyncio.run(run_mock_tts(host=args.host, port=args.port))
    else:
        parser.print_help()
        sys.exit(1)


async def run_client(url: str):
    """
    Run the Unity client simulator.

    Args:
        url: WebSocket URL of the backend
    """
    simulator = UnityClientSimulator(websocket_url=url)
    await simulator.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
