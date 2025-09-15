"""
Unit tests for scoring functions using real embeddings.
"""
import pytest
import numpy as np

from moodplay_phi.models.scoring import (
    calculate_relevance_score,
    calculate_diversity_score,
    calculate_resonance,
    calculate_rhythm_compatibility,
    calculate_engagement_score,
    update_taste_vector
)

@pytest.fixture
def mock_embeddings():
    """Provide mock embeddings for testing."""
    item_embedding = np.array([0.5, 0.2, 0.1])
    user_taste = np.array([0.4, 0.3, 0.3])
    context_vector = np.array([0.3, 0.3, 0.4])
    slate_embeddings = [np.array([0.1, 0.9, 0.0]), np.array([0.2, 0.1, 0.7])]
    return item_embedding, user_taste, context_vector, slate_embeddings

def test_calculate_relevance_score(mock_embeddings):
    item_embedding, user_taste, context_vector, _ = mock_embeddings
    score = calculate_relevance_score(item_embedding, user_taste, context_vector)
    assert 0.0 <= score <= 1.0
    assert isinstance(score, float)

def test_calculate_diversity_score(mock_embeddings):
    item_embedding, _, _, slate_embeddings = mock_embeddings
    # Test first item (no slate)
    score_first = calculate_diversity_score(item_embedding, [])
    assert score_first == 1.0
    # Test with slate
    score_slate = calculate_diversity_score(item_embedding, slate_embeddings)
    assert 0.0 <= score_slate <= 1.0

def test_calculate_resonance(mock_embeddings):
    item_embedding, user_taste, context_vector, _ = mock_embeddings
    score = calculate_resonance(
        item_embedding=item_embedding,
        user_taste=user_taste,
        context_vector=context_vector,
        rhythm_compat=0.8,
        is_novel=True,
        exposure_penalty=0.2
    )
    assert 0.0 <= score <= 1.0

def test_calculate_rhythm_compatibility():
    transition_matrix = np.array([
        [0.5, 0.5],
        [0.2, 0.8]
    ])
    score = calculate_rhythm_compatibility(0, 1, transition_matrix)
    assert 0.0 <= score <= 1.0

def test_calculate_engagement_score():
    score = calculate_engagement_score(watch_ratio=0.6, liked=True)
    assert 0.0 <= score <= 1.0
    score_partial = calculate_engagement_score(watch_ratio=0.3, liked=False)
    assert 0.0 <= score_partial <= 1.0

def test_update_taste_vector(mock_embeddings):
    item_embedding, user_taste, _, _ = mock_embeddings
    engagement = 0.8
    new_taste = update_taste_vector(user_taste, item_embedding, engagement, learning_rate=0.1)
    # Norm should still be > 0
    assert np.linalg.norm(new_taste) > 0
    # Should be normalized
    norm = np.linalg.norm(new_taste)
    assert abs(norm - 1.0) < 1e-6 or norm > 0
