#!/usr/bin/env python3
"""
Hybrid Memory System for AI Society

This module implements a sophisticated memory architecture with:
- Short-term: Rolling token buffer with LLM summarization
- Long-term: Vector store with recency and importance weights

Author: AI Society Contributors
License: MIT
"""

import os
import sys
import json
import time
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

import numpy as np
from sentence_transformers import SentenceTransformer

# Try to import vector stores
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime
    importance: float  # 0.0 to 1.0
    tokens: int
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.embedding is not None:
            data['embedding'] = self.embedding.tolist()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'embedding' in data and data['embedding']:
            data['embedding'] = np.array(data['embedding'])
        return cls(**data)

@dataclass
class MemorySummary:
    """Represents a summarized memory block"""
    id: str
    summary: str
    timespan: Tuple[datetime, datetime]
    original_entries: List[str]  # IDs of original entries
    importance: float
    tokens: int
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timespan'] = [self.timespan[0].isoformat(), self.timespan[1].isoformat()]
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemorySummary':
        """Create from dictionary"""
        data['timespan'] = (
            datetime.fromisoformat(data['timespan'][0]),
            datetime.fromisoformat(data['timespan'][1])
        )
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

class VectorStore(ABC):
    """Abstract base class for vector stores"""
    
    @abstractmethod
    async def add_memory(self, memory: MemoryEntry) -> None:
        """Add a memory to the vector store"""
        pass
    
    @abstractmethod
    async def search_memories(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[MemoryEntry, float]]:
        """Search for similar memories"""
        pass
    
    @abstractmethod
    async def delete_memory(self, memory_id: str) -> None:
        """Delete a memory from the store"""
        pass

class FAISSVectorStore(VectorStore):
    """FAISS-based vector store implementation"""
    
    def __init__(self, dimension: int = 384, index_path: str = "data/memory_index.faiss"):
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.id_to_memory: Dict[str, MemoryEntry] = {}
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        self.next_index = 0
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load FAISS index"""
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                # Load metadata
                metadata_path = self.index_path.replace('.faiss', '_metadata.json')
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        self.id_to_memory = {
                            k: MemoryEntry.from_dict(v) for k, v in metadata['memories'].items()
                        }
                        self.id_to_index = metadata['id_to_index']
                        self.index_to_id = {v: k for k, v in self.id_to_index.items()}
                        self.next_index = metadata['next_index']
                logger.info(f"✅ Loaded FAISS index with {len(self.id_to_memory)} memories")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load FAISS index: {e}, creating new one")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        logger.info(f"🆕 Created new FAISS index with dimension {self.dimension}")
    
    async def add_memory(self, memory: MemoryEntry) -> None:
        """Add a memory to FAISS"""
        if memory.embedding is None:
            logger.warning(f"⚠️ Memory {memory.id} has no embedding, skipping FAISS storage")
            return
        
        # Normalize embedding for cosine similarity
        embedding = memory.embedding / np.linalg.norm(memory.embedding)
        
        # Add to FAISS index
        self.index.add(embedding.reshape(1, -1))
        
        # Update mappings
        self.id_to_memory[memory.id] = memory
        self.id_to_index[memory.id] = self.next_index
        self.index_to_id[self.next_index] = memory.id
        self.next_index += 1
        
        # Save periodically
        if len(self.id_to_memory) % 10 == 0:
            await self._save_index()
        
        logger.debug(f"📥 Added memory {memory.id} to FAISS index")
    
    async def search_memories(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[MemoryEntry, float]]:
        """Search FAISS for similar memories"""
        if self.index.ntotal == 0:
            return []
        
        # Normalize query embedding
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search FAISS
        scores, indices = self.index.search(query_embedding.reshape(1, -1), min(k, self.index.ntotal))
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for invalid results
                continue
            
            memory_id = self.index_to_id.get(idx)
            if memory_id and memory_id in self.id_to_memory:
                memory = self.id_to_memory[memory_id]
                results.append((memory, float(score)))
        
        return results
    
    async def delete_memory(self, memory_id: str) -> None:
        """Delete memory from FAISS (by rebuilding index)"""
        if memory_id not in self.id_to_memory:
            return
        
        # Remove from mappings
        del self.id_to_memory[memory_id]
        if memory_id in self.id_to_index:
            del self.id_to_index[memory_id]
        
        # Rebuild index without the deleted memory
        await self._rebuild_index()
        logger.debug(f"🗑️ Deleted memory {memory_id} from FAISS")
    
    async def _rebuild_index(self):
        """Rebuild FAISS index from remaining memories"""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_to_index.clear()
        self.index_to_id.clear()
        self.next_index = 0
        
        for memory in self.id_to_memory.values():
            await self.add_memory(memory)
    
    async def _save_index(self):
        """Save FAISS index and metadata"""
        try:
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            metadata = {
                'memories': {k: v.to_dict() for k, v in self.id_to_memory.items()},
                'id_to_index': self.id_to_index,
                'next_index': self.next_index
            }
            metadata_path = self.index_path.replace('.faiss', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.debug(f"💾 Saved FAISS index with {len(self.id_to_memory)} memories")
        except Exception as e:
            logger.error(f"❌ Failed to save FAISS index: {e}")

class HybridMemorySystem:
    """
    Hybrid memory system with short-term buffer and long-term vector store
    """
    
    def __init__(
        self,
        short_term_token_limit: int = 4000,
        max_short_term_entries: int = 20,
        embedding_model: str = "all-MiniLM-L6-v2",
        vector_store_type: str = "faiss",
        session_id: str = None,
        memory_dir: str = "data/memory"
    ):
        self.short_term_token_limit = short_term_token_limit
        self.max_short_term_entries = max_short_term_entries
        self.session_id = session_id or f"session_{int(time.time())}"
        self.memory_dir = memory_dir
        
        # Ensure memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        # Short-term memory (rolling buffer)
        self.short_term_memories: List[MemoryEntry] = []
        self.running_summary: Optional[str] = None
        self.summary_history: List[MemorySummary] = []
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        logger.info(f"🧠 Loaded embedding model: {embedding_model}")
        
        # Initialize vector store
        self.vector_store = self._create_vector_store(vector_store_type)
        
        # Import OpenAI for summarization
        try:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.summarization_enabled = True
            logger.info("🤖 OpenAI summarization enabled")
        except ImportError:
            self.openai_client = None
            self.summarization_enabled = False
            logger.warning("⚠️ OpenAI not available, using simple summarization")
    
    def _create_vector_store(self, store_type: str) -> VectorStore:
        """Create vector store based on type"""
        if store_type == "faiss" and FAISS_AVAILABLE:
            index_path = os.path.join(self.memory_dir, f"memory_{self.session_id}.faiss")
            return FAISSVectorStore(
                dimension=self.embedding_model.get_sentence_embedding_dimension(),
                index_path=index_path
            )
        else:
            logger.warning(f"⚠️ Vector store {store_type} not available, using fallback")
            return FAISSVectorStore(dimension=384)  # Fallback
    
    async def add_memory(
        self,
        content: str,
        role: str,
        metadata: Dict[str, Any] = None,
        importance: float = None
    ) -> str:
        """Add a new memory entry"""
        
        # Generate embedding
        embedding = self.embedding_model.encode(content)
        
        # Calculate importance if not provided
        if importance is None:
            importance = await self._calculate_importance(content, role)
        
        # Estimate tokens (rough approximation)
        tokens = len(content.split()) * 1.3  # Approximate token count
        
        # Create memory entry
        memory = MemoryEntry(
            id=self._generate_id(content),
            content=content,
            role=role,
            timestamp=datetime.now(),
            importance=importance,
            tokens=int(tokens),
            metadata=metadata or {},
            embedding=embedding
        )
        
        # Add to short-term memory
        self.short_term_memories.append(memory)
        logger.debug(f"📝 Added memory to short-term: {memory.id}")
        
        # Check if we need to summarize and move to long-term
        await self._manage_memory_overflow()
        
        return memory.id
    
    async def retrieve_relevant_memories(
        self,
        query: str,
        k: int = 5,
        include_short_term: bool = True
    ) -> List[Tuple[str, float, str]]:  # (content, relevance, source)
        """Retrieve relevant memories for a query"""
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        relevant_memories = []
        
        # Search short-term memories
        if include_short_term:
            for memory in self.short_term_memories:
                if memory.embedding is not None:
                    similarity = np.dot(query_embedding, memory.embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(memory.embedding)
                    )
                    # Apply recency boost
                    recency_boost = self._calculate_recency_boost(memory.timestamp)
                    final_score = similarity * (1 + recency_boost)
                    
                    relevant_memories.append((
                        memory.content,
                        final_score,
                        f"short-term-{memory.role}"
                    ))
        
        # Search long-term vector store
        try:
            long_term_results = await self.vector_store.search_memories(query_embedding, k)
            for memory, score in long_term_results:
                # Apply importance and recency weights
                recency_boost = self._calculate_recency_boost(memory.timestamp)
                importance_boost = memory.importance * 0.2  # Scale importance
                final_score = score * (1 + recency_boost + importance_boost)
                
                relevant_memories.append((
                    memory.content,
                    final_score,
                    f"long-term-{memory.role}"
                ))
        except Exception as e:
            logger.warning(f"⚠️ Long-term memory search failed: {e}")
        
        # Include running summary if relevant
        if self.running_summary:
            summary_embedding = self.embedding_model.encode(self.running_summary)
            similarity = np.dot(query_embedding, summary_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(summary_embedding)
            )
            if similarity > 0.3:  # Threshold for relevance
                relevant_memories.append((
                    f"Previous conversation summary: {self.running_summary}",
                    similarity * 0.8,  # Slightly lower weight for summaries
                    "summary"
                ))
        
        # Sort by relevance and return top k
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        return relevant_memories[:k]
    
    async def get_context_for_query(self, query: str) -> str:
        """Get contextual information for a query"""
        
        # Retrieve relevant memories
        relevant_memories = await self.retrieve_relevant_memories(query, k=5)
        
        if not relevant_memories:
            return query
        
        # Build context
        context_parts = []
        
        # Add relevant memories
        for content, relevance, source in relevant_memories:
            if relevance > 0.3:  # Only include reasonably relevant memories
                context_parts.append(f"[{source}] {content[:200]}...")
        
        # Combine with current query
        if context_parts:
            context = "Context from conversation history:\n" + "\n".join(context_parts)
            context += f"\n\nCurrent query: {query}"
            return context
        
        return query
    
    async def _manage_memory_overflow(self):
        """Manage memory overflow by summarizing and moving to long-term storage"""
        
        # Check token limit
        total_tokens = sum(memory.tokens for memory in self.short_term_memories)
        
        if (total_tokens > self.short_term_token_limit or 
            len(self.short_term_memories) > self.max_short_term_entries):
            
            logger.info(f"🔄 Memory overflow detected: {total_tokens} tokens, {len(self.short_term_memories)} entries")
            await self._summarize_and_archive()
    
    async def _summarize_and_archive(self):
        """Summarize older memories and move them to long-term storage"""
        
        if len(self.short_term_memories) < 4:  # Need at least a few memories to summarize
            return
        
        # Take oldest memories for summarization (keep most recent ones in short-term)
        memories_to_archive = self.short_term_memories[:-10]  # Keep last 10 in short-term
        self.short_term_memories = self.short_term_memories[-10:]
        
        if not memories_to_archive:
            return
        
        # Generate summary of archived memories
        if self.summarization_enabled:
            summary_text = await self._generate_llm_summary(memories_to_archive)
        else:
            summary_text = self._generate_simple_summary(memories_to_archive)
        
        # Create summary object
        summary = MemorySummary(
            id=self._generate_id(summary_text),
            summary=summary_text,
            timespan=(memories_to_archive[0].timestamp, memories_to_archive[-1].timestamp),
            original_entries=[m.id for m in memories_to_archive],
            importance=max(m.importance for m in memories_to_archive),
            tokens=len(summary_text.split()) * 1.3,
            created_at=datetime.now()
        )
        
        self.summary_history.append(summary)
        self.running_summary = summary_text
        
        # Move individual memories to long-term storage
        for memory in memories_to_archive:
            try:
                await self.vector_store.add_memory(memory)
            except Exception as e:
                logger.warning(f"⚠️ Failed to add memory {memory.id} to long-term storage: {e}")
        
        logger.info(f"📦 Archived {len(memories_to_archive)} memories to long-term storage")
        logger.info(f"📋 Generated summary: {summary_text[:100]}...")
    
    async def _generate_llm_summary(self, memories: List[MemoryEntry]) -> str:
        """Generate summary using LLM"""
        
        if not self.openai_client:
            return self._generate_simple_summary(memories)
        
        # Prepare conversation text
        conversation_text = "\n".join([
            f"{memory.role.capitalize()}: {memory.content}"
            for memory in memories
        ])
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are summarizing a conversation for memory storage. Create a concise but comprehensive summary that captures key topics, decisions, and important details. Focus on information that would be useful for future reference."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this conversation:\n\n{conversation_text}"
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            summary = response.choices[0].message.content.strip()
            logger.debug(f"🤖 Generated LLM summary: {summary[:50]}...")
            return summary
            
        except Exception as e:
            logger.warning(f"⚠️ LLM summarization failed: {e}, using simple summary")
            return self._generate_simple_summary(memories)
    
    def _generate_simple_summary(self, memories: List[MemoryEntry]) -> str:
        """Generate simple summary without LLM"""
        
        user_messages = [m.content for m in memories if m.role == "user"]
        topics = []
        
        # Extract key topics from user messages
        for message in user_messages:
            # Simple keyword extraction
            words = message.lower().split()
            if any(word in words for word in ['function', 'code', 'python', 'programming']):
                topics.append("programming")
            elif any(word in words for word in ['math', 'calculate', 'equation']):
                topics.append("mathematics")
            elif any(word in words for word in ['explain', 'what', 'how', 'why']):
                topics.append("explanation")
        
        # Create summary
        unique_topics = list(set(topics))
        if unique_topics:
            summary = f"Conversation about {', '.join(unique_topics)}. "
        else:
            summary = "General conversation. "
        
        summary += f"Discussed {len(user_messages)} topics between {memories[0].timestamp.strftime('%H:%M')} and {memories[-1].timestamp.strftime('%H:%M')}."
        
        return summary
    
    async def _calculate_importance(self, content: str, role: str) -> float:
        """Calculate importance score for content"""
        
        importance = 0.5  # Base importance
        
        # Role-based importance
        if role == "user":
            importance += 0.1  # User queries are slightly more important
        
        # Content-based importance
        content_lower = content.lower()
        
        # High importance indicators
        if any(word in content_lower for word in ['error', 'problem', 'issue', 'fix', 'help']):
            importance += 0.3
        if any(word in content_lower for word in ['important', 'critical', 'urgent']):
            importance += 0.2
        if any(word in content_lower for word in ['code', 'function', 'algorithm', 'implementation']):
            importance += 0.1
        
        # Length-based importance (longer content often more important)
        if len(content) > 200:
            importance += 0.1
        elif len(content) < 50:
            importance -= 0.1
        
        return min(1.0, max(0.0, importance))
    
    def _calculate_recency_boost(self, timestamp: datetime) -> float:
        """Calculate recency boost for memory scoring"""
        
        age = datetime.now() - timestamp
        hours_old = age.total_seconds() / 3600
        
        # Recent memories get higher boost
        if hours_old < 1:
            return 0.3
        elif hours_old < 6:
            return 0.2
        elif hours_old < 24:
            return 0.1
        else:
            return 0.0
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:12]
    
    # Convenience methods for compatibility with web interface
    async def add_message(self, role: str, content: str, model: str = None, metadata: Dict = None):
        """Compatibility method for web interface"""
        msg_metadata = metadata or {}
        if model:
            msg_metadata['model'] = model
        
        return await self.add_memory(
            content=content,
            role=role,
            metadata=msg_metadata
        )
    
    def get_conversation_summary(self) -> str:
        """Get a brief summary of recent conversation"""
        if not self.short_term_memories:
            return "No previous conversation"
        
        # Use running summary if available
        if self.running_summary:
            return f"Running summary: {self.running_summary[:100]}..."
        
        # Extract recent topics from user messages
        recent_user_messages = [
            m.content for m in self.short_term_memories[-5:] 
            if m.role == 'user'
        ]
        
        if recent_user_messages:
            topics = []
            for msg in recent_user_messages:
                if len(msg) > 10:
                    # Extract first part of question/statement
                    topic = msg[:50].split('?')[0].split('.')[0]
                    topics.append(topic)
            
            if topics:
                return f"Recent topics: {', '.join(topics[-3:])}"
        
        return f"Conversation with {len(self.short_term_memories)} exchanges"
    
    @property
    def messages(self) -> List[Dict]:
        """Compatibility property for web interface - returns recent messages"""
        return [
            {
                'role': m.role,
                'content': m.content,
                'timestamp': m.timestamp.isoformat(),
                'model': m.metadata.get('model'),
                'metadata': m.metadata
            }
            for m in self.short_term_memories
        ]

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        
        short_term_tokens = sum(m.tokens for m in self.short_term_memories)
        
        return {
            "session_id": self.session_id,
            "short_term_memories": len(self.short_term_memories),
            "short_term_tokens": short_term_tokens,
            "token_limit": self.short_term_token_limit,
            "token_usage_percent": (short_term_tokens / self.short_term_token_limit) * 100,
            "summaries_created": len(self.summary_history),
            "running_summary": self.running_summary is not None,
            "long_term_storage": "faiss" if isinstance(self.vector_store, FAISSVectorStore) else "unknown",
            "summarization_enabled": self.summarization_enabled
        }

# Example usage
async def example_usage():
    """Example of how to use the hybrid memory system"""
    
    memory = HybridMemorySystem(
        short_term_token_limit=2000,
        max_short_term_entries=15,
        session_id="example_session"
    )
    
    # Add some memories
    await memory.add_memory("Hello, I'm learning Python programming", "user")
    await memory.add_memory("Great! Python is excellent for beginners. What would you like to learn first?", "assistant")
    await memory.add_memory("I want to learn about functions", "user")
    await memory.add_memory("Functions are fundamental in Python. Here's a simple example:\n\ndef greet(name):\n    return f'Hello, {name}!'", "assistant")
    
    # Retrieve relevant memories
    relevant = await memory.retrieve_relevant_memories("Can you explain that function?")
    print("🔍 Relevant memories:")
    for content, score, source in relevant:
        print(f"  [{source}] {score:.3f}: {content[:100]}...")
    
    # Get context for a query
    context = await memory.get_context_for_query("How do I make the function more complex?")
    print(f"\n📋 Context: {context[:200]}...")
    
    # Get statistics
    stats = memory.get_memory_stats()
    print(f"\n📊 Memory stats: {stats}")

if __name__ == "__main__":
    asyncio.run(example_usage())
