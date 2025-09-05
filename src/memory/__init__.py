"""
Memory Module for AI Society

This module provides sophisticated memory management for conversational AI:
- Short-term: Rolling token buffer with summarization
- Long-term: Vector store with semantic search
- Hybrid: Intelligent retrieval combining recency and relevance

Classes:
    HybridMemorySystem: Main memory management class
    MemoryEntry: Individual memory item
    MemorySummary: Summarized memory blocks
    VectorStore: Abstract base for vector storage
    FAISSVectorStore: FAISS implementation

Author: AI Society Contributors
License: MIT
"""

from .hybrid_memory import (
    HybridMemorySystem,
    MemoryEntry,
    MemorySummary,
    VectorStore,
    FAISSVectorStore
)

__all__ = [
    'HybridMemorySystem',
    'MemoryEntry', 
    'MemorySummary',
    'VectorStore',
    'FAISSVectorStore'
]
