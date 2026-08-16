import pytest

from app.fuzzy.controller import FuzzySpeedController
from app.fuzzy.explainability import explain_worked_example


def test_default_worked_example_pinned_values(fuzzy_controller: FuzzySpeedController):
    result = explain_worked_example(fuzzy_controller)
    assert result.fragility_val == 5.0
    assert result.bumpiness_val == 7.0
    assert result.mu_frag_moderate == pytest.approx(0.9983316649983317)
    assert result.mu_bump_moderate == pytest.approx(0.3333333333333333)
    assert result.mu_bump_rough == pytest.approx(0.25)
    assert result.rule5_strength == pytest.approx(0.3333333333333333)
    assert result.rule6_strength == pytest.approx(0.25)
    assert result.crisp_speed == pytest.approx(67.1984019054526)


def test_aggregated_curve_shape(fuzzy_controller: FuzzySpeedController):
    result = explain_worked_example(fuzzy_controller)
    from app.fuzzy.membership import SPEED_UNIVERSE

    assert result.aggregated_curve.shape == SPEED_UNIVERSE.shape
    max_strength = max(result.rule5_strength, result.rule6_strength)
    assert (result.aggregated_curve <= max_strength + 1e-9).all()


def test_custom_inputs_change_membership(fuzzy_controller: FuzzySpeedController):
    result = explain_worked_example(fuzzy_controller, fragility_val=0.0, bumpiness_val=0.0)
    assert result.mu_frag_moderate < 0.1
