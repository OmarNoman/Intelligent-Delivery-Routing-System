import pytest

from app.fuzzy.controller import FuzzySpeedController
from app.fuzzy.explainability import explain_inference, explain_worked_example


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


def test_explain_inference_matches_worked_example_at_default_inputs(fuzzy_controller: FuzzySpeedController):
    # Cross-check: at fragility=5/bumpiness=7, rules 5 and 6 are the only ones that should
    # fire, with strengths matching the hand-traced worked example.
    result = explain_inference(fuzzy_controller, 5.0, 7.0)
    fired = {r.rule_index: r for r in result.fired_rules}
    assert set(fired) == {5, 6}
    assert fired[5].strength == pytest.approx(0.3333333333333333)
    assert fired[6].strength == pytest.approx(0.25)
    assert result.crisp_speed == pytest.approx(67.1984019054526)


def test_explain_inference_robust_smooth_dominant(fuzzy_controller: FuzzySpeedController):
    # Near the low end of both inputs, only rule 1 (robust & smooth -> fast) should fire.
    result = explain_inference(fuzzy_controller, 0.0, 0.0)
    fired = {r.rule_index: r for r in result.fired_rules}
    assert set(fired) == {1}
    assert fired[1].fragility_term == "robust"
    assert fired[1].bumpiness_term == "smooth"
    assert fired[1].speed_term == "fast"
    assert fired[1].strength == pytest.approx(1.0)
