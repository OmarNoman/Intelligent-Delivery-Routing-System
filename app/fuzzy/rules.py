from skfuzzy import control as ctrl

# (fragility_term, bumpiness_term, speed_term), covering all 3x3 combinations.
# The Moderate fragility row deliberately produces distinct outputs from both the
# Robust and Fragile rows.
RULES = [
    ("robust", "smooth", "fast"),
    ("robust", "moderate", "fast"),
    ("robust", "rough", "medium"),
    ("moderate", "smooth", "fast"),
    ("moderate", "moderate", "medium"),
    ("moderate", "rough", "slow"),
    ("fragile", "smooth", "medium"),
    ("fragile", "moderate", "slow"),
    ("fragile", "rough", "slow"),
]


def build_ctrl_rules(
    fragility_ant: ctrl.Antecedent,
    bumpiness_ant: ctrl.Antecedent,
    speed_cons: ctrl.Consequent,
) -> list:
    return [
        ctrl.Rule(fragility_ant[frag_term] & bumpiness_ant[bump_term], speed_cons[speed_term])
        for frag_term, bump_term, speed_term in RULES
    ]
