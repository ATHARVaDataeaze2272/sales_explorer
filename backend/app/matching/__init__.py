"""
Matching module for client-prospect semantic matching
"""

from matching.matching_engine import MatchingEngine, MatchingStats
from matching.embeddings import EmbeddingService

__all__ = ['MatchingEngine', 'MatchingStats', 'EmbeddingService']