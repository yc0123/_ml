# Makefile for VTuber Backend

.PHONY: install dev-install clean test server client mock-gptsovits test-emotion test-tts test-llm

# Installation
install:
	pip install -r requirements.txt

dev-install:
	pip install -e .

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete

# Running
server:
	python -m vtuber_backend server

client:
	python -m vtuber_backend client

mock-gptsovits:
	python -m vtuber_backend mock-gptsovits

# Testing
test-emotion:
	python scripts/test_emotion_recognition.py

test-tts:
	python scripts/test_tts.py --use-mock

test-llm:
	python scripts/test_llm.py

# Help
help:
	@echo "Available commands:"
	@echo "  make install         - Install dependencies"
	@echo "  make dev-install     - Install package in development mode"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make server          - Run the server"
	@echo "  make client          - Run the client"
	@echo "  make test-emotion    - Test emotion recognition"
	@echo "  make test-tts        - Test TTS"
	@echo "  make test-llm        - Test LLM"
