from pydantic import BaseModel
from typing import Optional, List, Any


class ScoreRequest(BaseModel):
    prog_type: str
    inputs: dict[str, Any]


class ScoreFactorOut(BaseModel):
    name: str
    value: int
    max: int
    percent: float


class ScoreResultOut(BaseModel):
    score: int
    risk: str
    duration: int
    fpy: str
    inspection: str
    ppap: str
    recommendation: str
    factors: List[ScoreFactorOut]
    pra_forecast: str
    conformance: int


class ChecklistRequest(BaseModel):
    prog_type: str
    context: dict[str, Any]


class ChecklistItemOut(BaseModel):
    step: str
    text: str
    phase: str
    critical: bool
    warn: bool
    done: bool
    owner: str = ""
    due: str = ""


class ExportRequest(BaseModel):
    prog_type: str
    part_name: str
    customer_name: str
    result: ScoreResultOut
    checklist: List[ChecklistItemOut]
    meta: dict[str, Any]
