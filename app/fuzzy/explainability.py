from dataclasses import dataclass

import numpy as np
import skfuzzy as fuzz

from app.fuzzy.controller import FuzzySpeedController
from app.fuzzy.membership import BUMPINESS_UNIVERSE, FRAGILITY_UNIVERSE, bumpiness_mf, fragility_mf, speed_mf


@dataclass(frozen=True)
class WorkedExampleResult:
    fragility_val: float
    bumpiness_val: float
    mu_frag_moderate: float
    mu_bump_moderate: float
    mu_bump_rough: float
    rule5_strength: float  # moderate & moderate -> medium
    rule6_strength: float  # moderate & rough    -> slow
    crisp_speed: float
    aggregated_curve: np.ndarray


def explain_worked_example(
    controller: FuzzySpeedController, fragility_val: float = 5.0, bumpiness_val: float = 7.0
) -> WorkedExampleResult:
    mu_frag_mod = float(fuzz.interp_membership(FRAGILITY_UNIVERSE, fragility_mf("moderate"), fragility_val))
    mu_bump_mod = float(fuzz.interp_membership(BUMPINESS_UNIVERSE, bumpiness_mf("moderate"), bumpiness_val))
    mu_bump_rgh = float(fuzz.interp_membership(BUMPINESS_UNIVERSE, bumpiness_mf("rough"), bumpiness_val))

    r5_strength = min(mu_frag_mod, mu_bump_mod)
    r6_strength = min(mu_frag_mod, mu_bump_rgh)
    crisp_speed = controller.get_safe_speed(fragility_val, bumpiness_val)

    slow_mf = speed_mf("slow")
    medium_mf = speed_mf("medium")
    agg = np.fmax(np.fmin(r6_strength, slow_mf), np.fmin(r5_strength, medium_mf))

    return WorkedExampleResult(
        fragility_val=fragility_val,
        bumpiness_val=bumpiness_val,
        mu_frag_moderate=mu_frag_mod,
        mu_bump_moderate=mu_bump_mod,
        mu_bump_rough=mu_bump_rgh,
        rule5_strength=r5_strength,
        rule6_strength=r6_strength,
        crisp_speed=crisp_speed,
        aggregated_curve=agg,
    )
