import pytest

from app.fuzzy.membership import (
    BUMPINESS_MFS,
    BUMPINESS_UNIVERSE,
    FRAGILITY_MFS,
    FRAGILITY_UNIVERSE,
    SPEED_MFS,
    SPEED_UNIVERSE,
    bumpiness_mf,
    fragility_mf,
    speed_mf,
)


def test_universe_bounds_and_length():
    for universe, lo, hi in [
        (FRAGILITY_UNIVERSE, 0, 10),
        (BUMPINESS_UNIVERSE, 0, 10),
        (SPEED_UNIVERSE, 40, 100),
    ]:
        assert universe.min() == lo
        assert universe.max() == hi
        assert len(universe) == 1000


def test_mf_dicts_have_exactly_three_terms():
    assert set(FRAGILITY_MFS) == {"robust", "moderate", "fragile"}
    assert set(BUMPINESS_MFS) == {"smooth", "moderate", "rough"}
    assert set(SPEED_MFS) == {"slow", "medium", "fast"}


def test_mf_output_shape_matches_universe():
    assert fragility_mf("moderate").shape == FRAGILITY_UNIVERSE.shape
    assert bumpiness_mf("moderate").shape == BUMPINESS_UNIVERSE.shape
    assert speed_mf("medium").shape == SPEED_UNIVERSE.shape


def test_mf_peaks_near_one():
    # The 1000-point universe discretization means a triangle's peak x-value
    # doesn't always land exactly on a grid point, so this is a "close to 1"
    # check, not an exact one (same effect as the worked example's 0.998 vs 1.000).
    assert fragility_mf("moderate").max() == pytest.approx(1.0, abs=0.01)
    assert bumpiness_mf("moderate").max() == pytest.approx(1.0, abs=0.01)
    assert speed_mf("medium").max() == pytest.approx(1.0, abs=0.01)


def test_unknown_term_raises_keyerror():
    with pytest.raises(KeyError):
        fragility_mf("nonexistent")
