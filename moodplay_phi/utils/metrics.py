"""
Evaluation metrics for the recommendation system.
"""
from typing import List, Dict, Any, Set, Tuple
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

def calculate_precision(recommended: List[Any], relevant: Set[Any], k: int = None) -> float:
    """
    Calculate precision@k.
    
    Args:
        recommended: List of recommended items
        relevant: Set of relevant items
        k: Number of top items to consider. If None, use all recommended items.
        
    Returns:
        Precision score
    """
    if k is not None:
        recommended = recommended[:k]
    
    if not recommended:
        return 0.0
        
    relevant_recommended = len([item for item in recommended if item in relevant])
    return relevant_recommended / len(recommended)

def calculate_recall(recommended: List[Any], relevant: Set[Any], k: int = None) -> float:
    """
    Calculate recall@k.
    
    Args:
        recommended: List of recommended items
        relevant: Set of relevant items
        k: Number of top items to consider. If None, use all recommended items.
        
    Returns:
        Recall score
    """
    if k is not None:
        recommended = recommended[:k]
    
    if not relevant:
        return 1.0 if not recommended else 0.0
        
    relevant_recommended = len([item for item in recommended if item in relevant])
    return relevant_recommended / len(relevant)

def calculate_ndcg(recommended: List[Any], relevant: Set[Any], k: int = None) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain (NDCG)@k.
    
    Args:
        recommended: List of recommended items with relevance scores
        relevant: Dictionary of item_id to relevance score
        k: Number of top items to consider. If None, use all recommended items.
        
    Returns:
        NDCG score
    """
    if k is not None:
        recommended = recommended[:k]
    
    if not recommended:
        return 0.0
    
    # Calculate DCG
    dcg = 0.0
    for i, (item, rel) in enumerate(recommended, 1):
        dcg += (2 ** rel - 1) / np.log2(i + 1)
    
    # Calculate IDCG (Ideal DCG)
    ideal_recommended = sorted(
        [(item, rel) for item, rel in relevant.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    idcg = 0.0
    for i, (_, rel) in enumerate(ideal_recommended[:len(recommended)], 1):
        idcg += (2 ** rel - 1) / np.log2(i + 1)
    
    return dcg / idcg if idcg > 0 else 0.0

def calculate_diversity_score(
    item_embeddings: List[np.ndarray],
    k: int = None,
    min_diversity: float = 0.1
) -> float:
    """
    Calculate the diversity score of a set of item embeddings.
    
    Args:
        item_embeddings: List of item embedding vectors
        k: Number of items to consider. If None, use all items.
        min_diversity: Minimum diversity score to ensure some exploration
        
    Returns:
        Diversity score (0-1)
    """
    if not item_embeddings:
        return 0.0
        
    if k is not None:
        item_embeddings = item_embeddings[:k]
        
    if len(item_embeddings) == 1:
        return 1.0  # Maximum diversity for single item
        
    # Calculate pairwise cosine similarities
    embeddings_matrix = np.vstack(item_embeddings)
    similarities = cosine_similarity(embeddings_matrix)
    
    # Get upper triangle (excluding diagonal)
    upper_tri = np.triu_indices(len(item_embeddings), k=1)
    avg_similarity = np.mean(similarities[upper_tri])
    
    # Convert similarity to diversity (inverse)
    diversity = 1.0 - avg_similarity
    
    # Apply minimum diversity to ensure some exploration
    return max(diversity, min_diversity)

def calculate_serendipity(recommended: List[Any], popular: Set[Any], k: int = None) -> float:
    """
    Calculate serendipity of recommendations.
    
    Args:
        recommended: List of recommended items
        popular: Set of popular items
        k: Number of top items to consider. If None, use all recommended items.
        
    Returns:
        Serendipity score (fraction of recommended items that are not in popular items)
    """
    if k is not None:
        recommended = recommended[:k]
    
    if not recommended:
        return 0.0
        
    non_popular = [item for item in recommended if item not in popular]
    return len(non_popular) / len(recommended)
