import itertools

from skfuzzy import control as ctrl

from app.fuzzy.membership import BUMPINESS_MFS, FRAGILITY_MFS, SPEED_MFS
from app.fuzzy.rules import RULES, build_ctrl_rules


def test_rules_cover_all_nine_combinations():
    assert len(RULES) == 9
    pairs = {(frag, bump) for frag, bump, _ in RULES}
    expected = set(itertools.product(FRAGILITY_MFS.keys(), BUMPINESS_MFS.keys()))
    assert pairs == expected


def test_build_ctrl_rules_returns_nine_rule_objects():
    import numpy as np
    import skfuzzy as fuzz

    fragility = ctrl.Antecedent(np.linspace(0, 10, 100), "fragility")
    bumpiness = ctrl.Antecedent(np.linspace(0, 10, 100), "bumpiness")
    speed = ctrl.Consequent(np.linspace(40, 100, 100), "max_safe_speed")
    for term, params in FRAGILITY_MFS.items():
        fragility[term] = fuzz.trimf(fragility.universe, params)
    for term, params in BUMPINESS_MFS.items():
        bumpiness[term] = fuzz.trimf(bumpiness.universe, params)
    for term, params in SPEED_MFS.items():
        speed[term] = fuzz.trimf(speed.universe, params)

    rules = build_ctrl_rules(fragility, bumpiness, speed)
    assert len(rules) == 9
    assert all(isinstance(r, ctrl.Rule) for r in rules)
