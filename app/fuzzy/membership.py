import numpy as np
import skfuzzy as fuzz

FRAGILITY_UNIVERSE = np.linspace(0, 10, 1000)
BUMPINESS_UNIVERSE = np.linspace(0, 10, 1000)
# Bounds (40, 100) are a fuzzy-domain constant for the FIS output range, not tied to
# app.config's baseline/constraint speeds even though they numerically coincide today.
SPEED_UNIVERSE = np.linspace(40, 100, 1000)

FRAGILITY_MFS = {
    "robust": (0, 0, 4),
    "moderate": (2, 5, 8),
    "fragile": (6, 10, 10),
}
BUMPINESS_MFS = {
    "smooth": (0, 0, 4),
    "moderate": (2, 5, 8),
    "rough": (6, 10, 10),
}
SPEED_MFS = {
    "slow": (40, 40, 65),
    "medium": (50, 72.5, 95),
    "fast": (75, 100, 100),
}


def fragility_mf(term: str) -> np.ndarray:
    return fuzz.trimf(FRAGILITY_UNIVERSE, FRAGILITY_MFS[term])


def bumpiness_mf(term: str) -> np.ndarray:
    return fuzz.trimf(BUMPINESS_UNIVERSE, BUMPINESS_MFS[term])


def speed_mf(term: str) -> np.ndarray:
    return fuzz.trimf(SPEED_UNIVERSE, SPEED_MFS[term])
