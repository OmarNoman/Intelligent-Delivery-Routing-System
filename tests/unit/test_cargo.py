import dataclasses

import pytest

from app.models.cargo import CargoProfile


def test_known_labels():
    assert CargoProfile.from_fragility(2) == CargoProfile(fragility=2, label="Low")
    assert CargoProfile.from_fragility(5) == CargoProfile(fragility=5, label="Medium")
    assert CargoProfile.from_fragility(8) == CargoProfile(fragility=8, label="High")


def test_unknown_fragility_falls_back_to_str():
    assert CargoProfile.from_fragility(7).label == "7"
    assert CargoProfile.from_fragility(5.5).label == "5.5"


def test_frozen_dataclass():
    profile = CargoProfile.from_fragility(2)
    with pytest.raises(dataclasses.FrozenInstanceError):
        profile.label = "Changed"
