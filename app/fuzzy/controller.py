import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from app.fuzzy.membership import (
    BUMPINESS_MFS,
    BUMPINESS_UNIVERSE,
    FRAGILITY_MFS,
    FRAGILITY_UNIVERSE,
    SPEED_MFS,
    SPEED_UNIVERSE,
)
from app.fuzzy.rules import build_ctrl_rules


class FuzzySpeedController:
    # Encapsulates the Mamdani Fuzzy Inference System for calculating safe speeds
    # based on cargo fragility and road bumpiness

    def __init__(self) -> None:
        self.fragility = ctrl.Antecedent(FRAGILITY_UNIVERSE, "fragility")
        self.bumpiness = ctrl.Antecedent(BUMPINESS_UNIVERSE, "bumpiness")
        self.speed = ctrl.Consequent(SPEED_UNIVERSE, "max_safe_speed", defuzzify_method="centroid")

        for term, params in FRAGILITY_MFS.items():
            self.fragility[term] = fuzz.trimf(self.fragility.universe, params)
        for term, params in BUMPINESS_MFS.items():
            self.bumpiness[term] = fuzz.trimf(self.bumpiness.universe, params)
        for term, params in SPEED_MFS.items():
            self.speed[term] = fuzz.trimf(self.speed.universe, params)

        rules = build_ctrl_rules(self.fragility, self.bumpiness, self.speed)
        self.fis_ctrl = ctrl.ControlSystem(rules)
        self.fis_sim = ctrl.ControlSystemSimulation(self.fis_ctrl)

    def get_safe_speed(self, fragility_val: float, bumpiness_val: float) -> float:
        # Evaluates the FIS and returns crisp speed (km/h)
        self.fis_sim.input["fragility"] = float(np.clip(fragility_val, 0.01, 9.99))
        self.fis_sim.input["bumpiness"] = float(np.clip(bumpiness_val, 0.01, 9.99))
        self.fis_sim.compute()
        return float(self.fis_sim.output["max_safe_speed"])
