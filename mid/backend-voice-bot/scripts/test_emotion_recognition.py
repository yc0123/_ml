#!/usr/bin/env python3
"""
Test the emotion recognition component.
"""

import argparse
import cv2
import logging
import sys
import os
import time

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vtuber_backend.emotion.recognizer import EmotionRecognizer
from vtuber_backend.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Test the emotion recognition component."""
    # Configure logging
    setup_logging()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Test the emotion recognition component"
    )
    parser.add_argument("--camera", type=int, default=0, help="Camera ID to use")
    parser.add_argument(
        "--frequency", type=float, default=0.5, help="Detection frequency in seconds"
    )
    args = parser.parse_args()

    # Create emotion recognizer
    print("Starting emotion recognition test...")
    print("Press 'q' to quit")

    recognizer = EmotionRecognizer(
        camera_id=args.camera, detection_frequency=args.frequency
    )

    # Open webcam
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        logger.error(f"Failed to open camera {args.camera}")
        return

    try:
        # Main loop
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to capture frame")
                time.sleep(0.1)
                continue

            # Get current emotion
            emotion = recognizer.get_current_emotion()
            scores = recognizer.get_emotion_scores()

            # Display emotion on frame
            if emotion:
                # Format emotion scores
                score_text = ""
                if scores:
                    top_emotions = sorted(
                        scores.items(), key=lambda x: x[1], reverse=True
                    )[:3]
                    score_text = ", ".join([f"{e}: {s:.2f}" for e, s in top_emotions])

                # Add text to frame
                cv2.putText(
                    frame,
                    f"Emotion: {emotion}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

                cv2.putText(
                    frame,
                    score_text,
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    frame,
                    "No emotion detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

            # Display frame
            cv2.imshow("Emotion Recognition Test", frame)

            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            # Short sleep to prevent high CPU usage
            time.sleep(0.03)

    finally:
        # Clean up
        recognizer.stop()
        cap.release()
        cv2.destroyAllWindows()
        print("Emotion recognition test stopped")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error in emotion recognition test: {e}")
