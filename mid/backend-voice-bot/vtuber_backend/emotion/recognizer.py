#!/usr/bin/env python3
"""
Emotion recognition module using DeepFace.
"""
import logging
import threading
import time
from typing import Dict, Optional, Tuple

import cv2
import numpy as np
from deepface import DeepFace

logger = logging.getLogger(__name__)


class EmotionRecognizer:
    """Class for real-time emotion recognition using webcam and DeepFace."""

    def __init__(self, camera_id: int = 0, detection_frequency: float = 1.0):
        """
        Initialize the emotion recognizer.

        Args:
            camera_id: ID of the camera to use (default: 0 for primary webcam)
            detection_frequency: How often to detect emotions in seconds (default: 1.0)
        """
        self.camera_id = camera_id
        self.detection_frequency = detection_frequency
        self.current_emotion: Optional[str] = None
        self.emotion_scores: Dict[str, float] = {}
        self.running = False
        self.cap = None
        self.thread = None
        
        # Start the detection thread
        self.start()

    def start(self):
        """Start the emotion detection thread."""
        if self.running:
            return
            
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                return
                
            self.running = True
            self.thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.thread.start()
            logger.info("Emotion recognition started")
        except Exception as e:
            logger.error(f"Failed to start emotion recognition: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None

    def stop(self):
        """Stop the emotion detection thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
            
        if self.cap:
            self.cap.release()
            self.cap = None
            
        logger.info("Emotion recognition stopped")

    def get_current_emotion(self) -> Optional[str]:
        """Get the current dominant emotion."""
        return self.current_emotion

    def get_emotion_scores(self) -> Dict[str, float]:
        """Get all emotion scores."""
        return self.emotion_scores.copy()

    def _detection_loop(self):
        """Main detection loop running in a separate thread."""
        last_detection_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Only detect emotions at the specified frequency
                if current_time - last_detection_time < self.detection_frequency:
                    time.sleep(0.1)  # Short sleep to prevent CPU hogging
                    continue
                    
                last_detection_time = current_time
                
                # Capture frame
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    logger.warning("Failed to capture frame")
                    time.sleep(1.0)
                    continue
                
                # Detect emotion
                emotion, scores = self._detect_emotion(frame)
                
                # Update current emotion and scores
                self.current_emotion = emotion
                self.emotion_scores = scores
                
            except Exception as e:
                logger.error(f"Error in emotion detection loop: {e}")
                time.sleep(2.0)  # Wait longer on error

    def _detect_emotion(self, frame: np.ndarray) -> Tuple[Optional[str], Dict[str, float]]:
        """
        Detect emotion in a single frame.
        
        Args:
            frame: The frame to analyze
            
        Returns:
            Tuple of (dominant_emotion, emotion_scores)
        """
        try:
            # Analyze the frame with DeepFace
            result = DeepFace.analyze(
                frame, 
                actions=['emotion'],
                enforce_detection=False,  # Don't raise error if face not detected
                silent=True  # Suppress DeepFace logs
            )
            
            # Extract emotion data
            if isinstance(result, list) and len(result) > 0:
                emotion_data = result[0]['emotion']
                dominant_emotion = max(emotion_data.items(), key=lambda x: x[1])[0]
                return dominant_emotion, emotion_data
            else:
                return None, {}
                
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return None, {}