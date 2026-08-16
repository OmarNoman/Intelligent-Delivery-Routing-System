import pytest

from app.fuzzy.controller import FuzzySpeedController


def test_output_always_within_speed_bounds(fuzzy_controller: FuzzySpeedController):
    for fragility in (0.0, 2.5, 5.0, 7.5, 10.0):
        for bumpiness in (0.0, 2.5, 5.0, 7.5, 10.0):
            speed = fuzzy_controller.get_safe_speed(fragility, bumpiness)
            assert 40.0 <= speed <= 100.0


def test_pinned_worked_example_speed(fuzzy_controller: FuzzySpeedController):
    assert fuzzy_controller.get_safe_speed(5.0, 7.0) == pytest.approx(67.1984019054526)


def test_clips_out_of_range_inputs(fuzzy_controller: FuzzySpeedController):
    assert fuzzy_controller.get_safe_speed(-5, -5) == pytest.approx(
        fuzzy_controller.get_safe_speed(0.01, 0.01)
    )
    assert fuzzy_controller.get_safe_speed(-5, -5) == pytest.approx(91.66659666629332)
    assert fuzzy_controller.get_safe_speed(15, 15) == pytest.approx(
        fuzzy_controller.get_safe_speed(9.99, 9.99)
    )
    assert fuzzy_controller.get_safe_speed(15, 15) == pytest.approx(48.33340333370662)


def test_robust_smooth_faster_than_fragile_rough(fuzzy_controller: FuzzySpeedController):
    assert fuzzy_controller.get_safe_speed(0, 0) > fuzzy_controller.get_safe_speed(10, 10)
