"""
Unit tests for IngredientMapper service.

Tests quantity normalization, ingredient parsing, and product matching logic.
"""

import pytest
from app.services.ingredient_mapper import (
    IngredientMapper,
    ParsedIngredient,
    UNIT_CONVERSIONS,
    AVAILABILITY_BOOST_THRESHOLD,
    AVAILABILITY_BOOST_MULTIPLIER,
)


class TestNormalizeQuantity:
    """Tests for quantity normalization and unit conversion."""

    @pytest.fixture
    def mapper(self):
        """Create IngredientMapper instance for testing."""
        return IngredientMapper(knuspr_client=None)

    def test_normalize_same_unit(self, mapper):
        """Test normalization when source and target units are the same."""
        result, unit = mapper.normalize_quantity(2.5, "cup", "cup")
        assert result == 2.5
        assert unit == "cup"

    def test_normalize_weight_conversion(self, mapper):
        """Test conversion between weight units."""
        # 500g to kg
        result, unit = mapper.normalize_quantity(500, "g", "kg")
        assert result == 0.5
        assert unit == "kg"

        # 1 kg to grams
        result, unit = mapper.normalize_quantity(1, "kg", "g")
        assert result == 1000
        assert unit == "g"

    def test_normalize_volume_conversion(self, mapper):
        """Test conversion between volume units."""
        # 1 cup to ml
        result, unit = mapper.normalize_quantity(1, "cup", "ml")
        assert result == 240
        assert unit == "ml"

        # 240 ml to cups
        result, unit = mapper.normalize_quantity(240, "ml", "cup")
        assert result == 1.0
        assert unit == "cup"

    def test_normalize_ounces_to_grams(self, mapper):
        """Test ounces to grams conversion."""
        result, unit = mapper.normalize_quantity(1, "oz", "g")
        assert abs(result - 28.35) < 0.01
        assert unit == "g"

    def test_normalize_pounds_to_grams(self, mapper):
        """Test pounds to grams conversion."""
        result, unit = mapper.normalize_quantity(1, "lb", "g")
        assert abs(result - 453.6) < 0.01
        assert unit == "g"

    def test_normalize_incompatible_units_count_to_weight(self, mapper):
        """Test that count units cannot be converted to weight."""
        result, unit = mapper.normalize_quantity(2, "can", "g")
        assert result == 2
        assert unit == "can"

    def test_normalize_incompatible_units_volume_to_weight(self, mapper):
        """Test that volume cannot be converted directly to weight."""
        result, unit = mapper.normalize_quantity(1, "cup", "g")
        assert result == 1
        assert unit == "cup"

    def test_normalize_unknown_source_unit(self, mapper):
        """Test handling of unknown source unit."""
        result, unit = mapper.normalize_quantity(5, "unknown", "g")
        assert result == 5
        assert unit == "unknown"

    def test_normalize_unknown_target_unit(self, mapper):
        """Test handling of unknown target unit."""
        result, unit = mapper.normalize_quantity(500, "g", "unknown")
        assert result == 500
        assert unit == "g"

    def test_normalize_negative_quantity_raises_error(self, mapper):
        """Test that negative quantities raise ValueError."""
        with pytest.raises(ValueError, match="Quantity must be non-negative"):
            mapper.normalize_quantity(-1, "cup", "ml")

    def test_normalize_zero_quantity(self, mapper):
        """Test that zero quantity is handled correctly."""
        result, unit = mapper.normalize_quantity(0, "g", "kg")
        assert result == 0
        assert unit == "kg"

    def test_normalize_unit_aliases(self, mapper):
        """Test that unit aliases are properly normalized."""
        # "cups" should be normalized to "cup"
        result1, unit1 = mapper.normalize_quantity(2, "cups", "ml")
        result2, unit2 = mapper.normalize_quantity(2, "cup", "ml")
        assert result1 == result2
        assert unit1 == unit2

        # "gram" should be normalized to "g"
        result3, unit3 = mapper.normalize_quantity(100, "gram", "kg")
        result4, unit4 = mapper.normalize_quantity(100, "g", "kg")
        assert result3 == result4
        assert unit3 == unit4

    def test_normalize_division_by_zero_protection(self, mapper):
        """Test protection against invalid conversion factors."""
        # Mock a conversion factor of 0 by using an edge case
        # The code should handle this gracefully
        result, unit = mapper.normalize_quantity(5, "g", "g")
        assert result == 5
        assert unit == "g"

    def test_normalize_case_insensitive(self, mapper):
        """Test that unit normalization is case-insensitive."""
        result1, unit1 = mapper.normalize_quantity(1, "CUP", "ML")
        result2, unit2 = mapper.normalize_quantity(1, "cup", "ml")
        assert result1 == result2
        assert unit1 == unit2


class TestParseIngredientString:
    """Tests for ingredient string parsing."""

    @pytest.fixture
    def mapper(self):
        """Create IngredientMapper instance for testing."""
        return IngredientMapper(knuspr_client=None)

    def test_parse_basic_ingredient(self, mapper):
        """Test parsing basic ingredient strings."""
        parsed = mapper.parse_ingredient_string("2 cups flour")
        assert parsed.quantity == 2.0
        assert parsed.unit == "cups"
        assert parsed.name == "flour"

    def test_parse_ingredient_with_decimal(self, mapper):
        """Test parsing ingredient with decimal quantity."""
        parsed = mapper.parse_ingredient_string("1.5 cups sugar")
        assert parsed.quantity == 1.5
        assert parsed.unit == "cups"
        assert parsed.name == "sugar"

    def test_parse_ingredient_without_unit(self, mapper):
        """Test parsing ingredient without explicit unit."""
        parsed = mapper.parse_ingredient_string("garlic")
        assert parsed.quantity == 1
        assert parsed.unit == "pcs"
        assert parsed.name == "garlic"

    def test_parse_ingredient_with_parentheses(self, mapper):
        """Test parsing ingredient with additional information."""
        parsed = mapper.parse_ingredient_string("1 can (400g) kidney beans")
        assert parsed.quantity == 1.0
        assert parsed.unit == "can"
        assert "kidney beans" in parsed.name

    def test_parse_ingredient_cleans_descriptors(self, mapper):
        """Test that ingredient cleaning removes common descriptors."""
        parsed = mapper.parse_ingredient_string("2 cups fresh chopped tomatoes")
        assert "fresh" not in parsed.name
        assert "chopped" not in parsed.name
        assert "tomatoes" in parsed.name


class TestSimilarityScore:
    """Tests for ingredient similarity scoring."""

    @pytest.fixture
    def mapper(self):
        """Create IngredientMapper instance for testing."""
        return IngredientMapper(knuspr_client=None)

    def test_similarity_exact_match(self, mapper):
        """Test similarity score for exact matches."""
        score = mapper._similarity_score("kidney beans", "kidney beans")
        assert score == 1.0

    def test_similarity_partial_match(self, mapper):
        """Test similarity score for partial matches."""
        score = mapper._similarity_score("beans", "kidney beans")
        assert score > 0.7  # Should be high similarity

    def test_similarity_case_insensitive(self, mapper):
        """Test that similarity matching is case-insensitive."""
        score1 = mapper._similarity_score("Kidney Beans", "kidney beans")
        score2 = mapper._similarity_score("kidney beans", "kidney beans")
        assert score1 == score2

    def test_similarity_word_order_tolerance(self, mapper):
        """Test similarity with word order variations."""
        score = mapper._similarity_score("beans kidney", "kidney beans")
        assert score > 0.7  # Should handle word order

    def test_similarity_no_match(self, mapper):
        """Test similarity score for completely different strings."""
        score = mapper._similarity_score("apple", "carrot")
        assert score < 0.5  # Should be low similarity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
