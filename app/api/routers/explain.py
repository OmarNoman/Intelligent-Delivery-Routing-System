from fastapi import APIRouter, Depends

from app.api.dependencies import get_controller
from app.fuzzy.controller import FuzzySpeedController
from app.fuzzy.explainability import explain_inference
from app.models.schemas import ExplainRequest, ExplainResponse, FiredRuleOut

router = APIRouter(tags=["explain"])


@router.post("/explain", response_model=ExplainResponse)
def explain(req: ExplainRequest, controller: FuzzySpeedController = Depends(get_controller)) -> ExplainResponse:
    result = explain_inference(controller, req.fragility, req.bumpiness)
    return ExplainResponse(
        fragility=result.fragility_val,
        bumpiness=result.bumpiness_val,
        fragility_memberships=result.fragility_memberships,
        bumpiness_memberships=result.bumpiness_memberships,
        fired_rules=[
            FiredRuleOut(
                rule_index=r.rule_index,
                fragility_term=r.fragility_term,
                bumpiness_term=r.bumpiness_term,
                speed_term=r.speed_term,
                strength=r.strength,
            )
            for r in result.fired_rules
        ],
        crisp_speed=result.crisp_speed,
    )
