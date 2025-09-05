#!/usr/bin/env python3
"""
AI Society - Routing Package

Intelligent routing components for dynamic model selection.
Includes local routing, OpenAI meta-routing, and enhanced routing capabilities.

Author: AI Society Contributors
License: MIT
"""

from .intelligent_router import IntelligentRouter
from .enhanced_intelligent_router import EnhancedIntelligentRouter
from .openai_meta_router import OpenAIMetaRouter

__all__ = ['IntelligentRouter', 'EnhancedIntelligentRouter', 'OpenAIMetaRouter']
