#!/usr/bin/env python3
"""
AI Society - Model Discovery Package

Automated model discovery and management for the Ollama library.
Provides background scanning, performance tracking, and model registry management.

Author: AI Society Contributors
License: MIT
"""

from .model_discovery import ModelDiscoveryDaemon, OllamaLibraryScanner

__all__ = ['ModelDiscoveryDaemon', 'OllamaLibraryScanner']
