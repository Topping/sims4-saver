.PHONY: deps build clean

# Detect OS
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

# Version from environment or default
VERSION ?= dev

deps:
	uv sync

build: deps
ifeq ($(DETECTED_OS),Windows)
	uv run pyinstaller sims-saver.spec
	@echo "Built: dist/Sims4-Save-Helper.exe"
else ifeq ($(DETECTED_OS),Darwin)
	uv run pyinstaller sims-saver.spec
	@echo "Built: dist/Sims4-Save-Helper.app"
else
	@echo "Unsupported OS: $(DETECTED_OS)"
	@exit 1
endif

clean:
	rm -rf build dist __pycache__
	find . -name "*.pyc" -delete
