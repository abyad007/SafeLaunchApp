from fastapi import APIRouter
from core.customer_rules import CUSTOMER_RULES

router = APIRouter()

PROGRAM_LABELS = {
    "new":        "New Program",
    "new_plant":  "New Plant Launch",
    "transfer":   "Business Transfer",
    "my_change":  "MY Change / Engineering Change",
    "restart":    "Restart After Shutdown",
    "absence":    "Absence / Turnover (High)",
    "capacity":   "Capacity Change",
}

@router.get("/program-types")
def get_program_types():
    return [{"value": k, "label": v} for k, v in PROGRAM_LABELS.items()]

@router.get("/customers")
def get_customers():
    return [
        {"value": k, "label": v["name"], "color": v.get("color", "#16283F"), "gates": v.get("gates", [])}
        for k, v in CUSTOMER_RULES.items()
        if k not in ("default", "other")
    ]
