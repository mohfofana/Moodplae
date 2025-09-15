"""
Scoring functions for MoodPlay Phi.
"""
from typing import Dict, List, Tuple, Optional, Set
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity

def calculate_relevance_score(item_embedding: np.ndarray, 
                           user_taste: np.ndarray, 
                           context_vector: np.ndarray) -> float:
    """
    Calculate relevance score for an item based on user taste and context.
    
    Args:
        item_embedding: Item's embedding vector
        user_taste: User's taste vector
        context_vector: Current context vector
        
    Returns:
        Relevance score (0-1)
    """
    # Combine user taste and context
    target_vector = 0.7 * user_taste + 0.3 * context_vector
    
    # Calculate cosine similarity
    similarity = float(sk_cosine_similarity(
        item_embedding.reshape(1, -1), 
        target_vector.reshape(1, -1)
    )[0][0])
    
    # Convert from [-1, 1] to [0, 1] range
    return (similarity + 1) / 2

def calculate_diversity_score(
    candidate_embedding: np.ndarray, 
    slate_embeddings: List[np.ndarray], 
    min_diversity: float = 0.1
) -> float:
    """
    Calculate diversity score for a candidate item relative to existing slate.
    
    Args:
        candidate_embedding: Embedding of candidate item
        slate_embeddings: List of embeddings of items already in slate
        min_diversity: Minimum diversity to ensure some exploration
        
    Returns:
        Diversity score (0-1)
    """
    if not slate_embeddings:
        return 1.0  # Maximum diversity for first item
    
    # Calculate average similarity to existing items
    similarities = [
        sk_cosine_similarity(
            candidate_embedding.reshape(1, -1),
            item.reshape(1, -1)
        )[0][0] 
        for item in slate_embeddings
    ]
    
    avg_similarity = np.mean(similarities) if similarities else 0
    
    # Convert similarity to diversity (inverse)
    diversity = 1.0 - avg_similarity
    
    # Apply minimum diversity to ensure some exploration
    return max(diversity, min_diversity)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
        
    Returns:
        Cosine similarity between a and b
    """
    return float(sk_cosine_similarity(a.reshape(1, -1), b.reshape(1, -1))[0][0])

def calculate_resonance(
    item_embedding: np.ndarray,
    user_taste: np.ndarray,
    context_vector: np.ndarray,
    rhythm_compat: float,
    is_novel: bool,
    exposure_penalty: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate the resonance score for an item.
    
    Resonance combines multiple factors:
    - Alignment with user's taste
    - Contextual fit
    - Rhythm compatibility
    - Novelty boost
    - Exposure penalty
    
    Args:
        item_embedding: Item's embedding vector
        user_taste: User's taste vector
        context_vector: Current context vector
        rhythm_compat: Rhythm compatibility score (0-1)
        is_novel: Whether the item is novel to the user
        exposure_penalty: Exposure penalty (0-1)
        weights: Optional weights for each component
        
    Returns:
        Resonance score (higher is better)
    """
    if weights is None:
        weights = {
            'taste': 3.0,      # Weight for taste alignment
            'context': 2.0,    # Weight for context alignment
            'rhythm': 1.5,     # Weight for rhythm compatibility
            'novelty': 1.0,    # Base weight for novelty boost
            'exposure': 1.0    # Weight for exposure penalty
        }
    
    # Calculate individual components
    taste_align = cosine_similarity(item_embedding, user_taste)
    context_align = cosine_similarity(item_embedding, context_vector)
    
    # Calculate novelty boost (higher for novel items)
    novelty_boost = 0.0
    if is_novel:
        # Scale novelty boost by how novel the item is (0.5 to 1.5)
        novelty_boost = 0.5 + cosine_similarity(item_embedding, user_taste)
    
    # Combine components with weights
    score = (
        weights['taste'] * taste_align +
        weights['context'] * context_align +
        weights['rhythm'] * rhythm_compat +
        (weights['novelty'] * novelty_boost if is_novel else 0.0) -
        weights['exposure'] * exposure_penalty
    )
    
    # Normalize to 0-1 range
    total_weight = sum(w for k, w in weights.items() if k != 'novelty' or is_novel)
    if total_weight > 0:
        score = max(0.0, min(1.0, (score + total_weight) / (2 * total_weight)))
    
    return score

def calculate_rhythm_compatibility(
    current_facet: int,
    candidate_facet: int,
    transition_matrix: np.ndarray,
    base_prob: float = 0.1
) -> float:
    """
    Calculate rhythm compatibility between current and candidate facets.
    
    Args:
        current_facet: Index of current facet
        candidate_facet: Index of candidate facet
        transition_matrix: KxK transition matrix
        base_prob: Base probability for smoothing
        
    Returns:
        Rhythm compatibility score (0-1)
    """
    if transition_matrix.ndim != 2 or transition_matrix.shape[0] != transition_matrix.shape[1]:
        raise ValueError("transition_matrix must be a square matrix")
    
    K = transition_matrix.shape[0]
    if current_facet < 0 or current_facet >= K or candidate_facet < 0 or candidate_facet >= K:
        raise ValueError("Facet indices out of bounds")
    
    # Get transition probability with additive smoothing
    p = transition_matrix[current_facet, candidate_facet]
    return (p + base_prob) / (1 + base_prob * K)

def calculate_diversity(
    candidate_embedding: np.ndarray,
    slate_embeddings: List[np.ndarray],
    min_diversity: float = 0.1
) -> float:
    """
    Calculate diversity of candidate relative to items already in the slate.
    
    Args:
        candidate_embedding: Embedding of candidate item
        slate_embeddings: List of embeddings of items already in slate
        min_diversity: Minimum diversity to ensure some exploration
        
    Returns:
        Diversity score (0-1)
    """
    if not slate_embeddings:
        return 1.0  # Maximum diversity for first item
    
    # Calculate average similarity to items in slate
    similarities = [
        cosine_similarity(candidate_embedding, e) 
        for e in slate_embeddings
    ]
    
    avg_similarity = np.mean(similarities) if similarities else 0.0
    return max(min_diversity, 1.0 - avg_similarity)

def calculate_engagement_score(
    watch_ratio: float,
    liked: bool,
    base_engagement: float = 0.3,
    like_boost: float = 0.3
) -> float:
    """
    Calculate engagement score from user interaction.
    
    Args:
        watch_ratio: Portion of content watched (0-1)
        liked: Whether the user liked the item
        base_engagement: Base engagement for partial watches
        like_boost: Additional engagement boost for likes
        
    Returns:
        Engagement score (0-1)
    """
    engagement = min(1.0, base_engagement + watch_ratio * (1.0 - base_engagement))
    if liked:
        engagement = min(1.0, engagement + like_boost)
    return engagement

def update_taste_vector(
    current_taste: np.ndarray,
    item_embedding: np.ndarray,
    engagement: float,
    learning_rate: float = 0.1
) -> np.ndarray:
    """
    Update user taste vector based on engagement with an item.
    
    Args:
        current_taste: Current taste vector
        item_embedding: Embedding of interacted item
        engagement: Engagement score (0-1)
        learning_rate: Maximum learning rate
        
    Returns:
        Updated taste vector (normalized)
    """
    # Scale update by engagement
    update = learning_rate * engagement * (item_embedding - current_taste)
    new_taste = current_taste + update
    
    # Renormalize
    norm = np.linalg.norm(new_taste)
    if norm > 0:
        new_taste = new_taste / norm
    
    return new_taste
