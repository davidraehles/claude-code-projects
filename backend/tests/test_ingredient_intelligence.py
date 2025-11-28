"""
Basic tests for Ingredient Intelligence system.

Tests the agent functionality without full database setup.
"""

import pytest
from app.agents.ingredient_intelligence import IngredientIntelligenceAgent


def test_normalize_ingredient_name():
    """Test ingredient name normalization."""
    agent = IngredientIntelligenceAgent(db_session=None)

    # Test basic normalization
    assert agent.normalize_ingredient_name("Fresh Spinach") == "spinach"
    assert agent.normalize_ingredient_name("Chopped Onions") == "onions"
    assert agent.normalize_ingredient_name("  Garlic   ") == "garlic"

    # Test with units
    assert agent.normalize_ingredient_name("500g Flour") == "flour"
    assert agent.normalize_ingredient_name("2 cups Sugar") == "sugar"

    # Test with adjectives
    assert agent.normalize_ingredient_name("Fresh Diced Tomatoes") == "tomatoes"


def test_agent_imports():
    """Test that agent can be imported."""
    from app.agents.ingredient_intelligence import IngredientIntelligenceAgent
    assert IngredientIntelligenceAgent is not None


def test_api_imports():
    """Test that API endpoints can be imported."""
    from app.api.v1.ingredients import router
    assert router is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
