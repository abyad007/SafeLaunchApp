import sys
from pathlib import Path

_backend = Path(__file__).parent
_root = _backend.parent
sys.path.insert(0, str(_root))    # core/ lives here
sys.path.insert(0, str(_backend)) # routers/ lives here

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import score, plan, export, meta

app = FastAPI(title="SafeLaunch API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router,   prefix="/api")
app.include_router(score.router,  prefix="/api")
app.include_router(plan.router,   prefix="/api")
app.include_router(export.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
