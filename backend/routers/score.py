from fastapi import APIRouter, HTTPException
from dataclasses import asdict
from sys import path as syspath
from pathlib import Path

syspath.insert(0, str(Path(__file__).parent.parent.parent / "SafeLaunchApp"))

from core.scoring_engine import calculate_score
from models import ScoreRequest, ScoreResultOut, ScoreFactorOut

router = APIRouter()


@router.post("/score", response_model=ScoreResultOut)
def score(req: ScoreRequest):
    try:
        result = calculate_score(req.prog_type, req.inputs)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ScoreResultOut(
        score=result.score,
        risk=result.risk,
        duration=result.duration,
        fpy=result.fpy,
        inspection=result.inspection,
        ppap=result.ppap,
        recommendation=result.recommendation,
        pra_forecast=result.pra_forecast or "",
        conformance=result.conformance or 0,
        factors=[
            ScoreFactorOut(
                name=f.name,
                value=f.value,
                max=f.max,
                percent=round(f.value / f.max * 100) if f.max else 0,
            )
            for f in result.factors
        ],
    )
