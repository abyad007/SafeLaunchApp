# core/scoring_engine.py
# ─────────────────────────────────────────────────────────────────────────────
# Contains one scoring function per program type.
# Each function receives a dict of user inputs and returns a dict of results.
#
# Python syntax reminders used in this file:
#   def func(param: type) -> type:   defines a function with type hints
#   """..."""                          docstring — describes what the function does
#   dict.get(key, default)            safe dict lookup
#   list.append(item)                 adds item to end of list
#   min(a, b)                         returns the smaller value
#   f"text {variable}"                f-string — embeds a variable in a string
# ─────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass, field  # dataclass = cleaner way to define data structures
from typing import List                    # used for type hints on lists


# ── Data structures ──────────────────────────────────────────────────────────
# @dataclass automatically generates __init__, __repr__ etc.
# This is cleaner than plain dicts for structured return values.

@dataclass
class ScoreFactor:
    """One risk factor contribution — name, points earned, max possible."""
    name:  str
    value: int
    max:   int

    # Property: computed attribute — access like .percent, no parentheses needed
    @property
    def percent(self) -> float:
        """Returns what % of the max this factor scored."""
        return round(self.value / self.max * 100, 1) if self.max else 0


@dataclass
class ScoreResult:
    """Full result returned by every scoring function."""
    score:       int                          # 0–100 total risk score
    risk:        str                          # "LOW", "MEDIUM", "HIGH"
    duration:    int                          # safe launch window in days
    fpy:         str                          # First Pass Yield range
    inspection:  str                          # inspection method
    ppap:        str                          # PPAP level
    recommendation: str                       # text recommendation
    factors:     List[ScoreFactor] = field(default_factory=list)  # list of factors
    pra_forecast: str = ""                    # BT-specific PRA status
    conformance:  int = 0                     # BT-specific conformance %


# ── Helper: apply risk classification ────────────────────────────────────────

def _classify(score: int) -> dict:
    """
    Given a score 0-100, returns the risk level + launch parameters.
    The underscore prefix (_classify) means "private — only used inside this file".
    """
    if score >= 70:
        return {
            "risk":           "HIGH",
            "duration":       120,
            "fpy":            "93–95%",
            "inspection":     "100% Inspection",
            "ppap":           "Level 3",
            "recommendation": (
                "High-risk program — intensive safe launch. "
                "Activate 100% end-of-line containment, assign dedicated quality engineer, "
                "hold weekly management reviews until exit criteria confirmed."
            ),
        }
    elif score >= 40:
        return {
            "risk":           "MEDIUM",
            "duration":       60,
            "fpy":            "96–98%",
            "inspection":     "Critical Characteristics",
            "ppap":           "Level 2",
            "recommendation": (
                "Medium-risk — standard safe launch protocol. "
                "Focus on critical characteristics. Bi-weekly reviews. "
                "Resolve all open PFMEA actions before start date."
            ),
        }
    else:
        return {
            "risk":           "LOW",
            "duration":       30,
            "fpy":            "98–99.5%",
            "inspection":     "Statistical Sampling (AQL 1.0)",
            "ppap":           "Level 1",
            "recommendation": (
                "Low-risk — minimal safe launch protocol. "
                "Apply AQL sampling. Verify MSA complete and control plan reviewed."
            ),
        }


# ═════════════════════════════════════════════════════════════════════════════
# 1. NEW PROGRAM  (per EANP_4-1_CS_01-03_EN)
# ═════════════════════════════════════════════════════════════════════════════

def score_new_program(inputs: dict) -> ScoreResult:
    """
    Scores a New Program launch.

    Based on general quality risk factors — no procedure-specific
    methodology assumed. Upload your own procedure to data/procedures/
    to customise the checklist.

    Expected input keys:
        headcount      : int — estimated operators in line at SOP
        np_experience  : "known" | "medium" | "new"
        pfmea          : int 1–10
        volume         : int (pcs/day)
        critical       : "yes" | "no"  (Special Characteristics applied)
        prod_system    : "batch" | "ksk"
        customer_bonus : int
        customer_name  : str
    """
    factors: List[ScoreFactor] = []
    score = 0

    # 1) Estimated headcount — larger teams = more training and flexibility risk
    hc = int(inputs.get("headcount") or 0)
    if hc > 0:
        hc_score = 14 if hc > 80 else (10 if hc > 40 else (5 if hc > 15 else 2))
        score += hc_score
        factors.append(ScoreFactor(f"Operator Headcount ({hc})", hc_score, 14))

    # 2) Team / customer experience — new relationship = higher risk
    exp_map = {"known": 0, "medium": 12, "new": 22}
    exp_score = exp_map.get(inputs.get("np_experience", "medium"), 12)
    if exp_score > 0:
        score += exp_score
        factors.append(ScoreFactor("Team / Customer Experience", exp_score, 22))

    # 3) PFMEA Severity
    pfmea = int(inputs.get("pfmea") or 5)
    pf_score = 16 if pfmea >= 9 else (12 if pfmea >= 7 else (7 if pfmea >= 5 else 3))
    score += pf_score
    factors.append(ScoreFactor(f"PFMEA Severity ({pfmea})", pf_score, 16))

    # 4) Volume
    vol = int(inputs.get("volume") or 0)
    vol_score = 10 if vol > 5000 else (6 if vol > 1000 else 3)
    score += vol_score
    factors.append(ScoreFactor("Volume / Day", vol_score, 10))

    # 5) Special Characteristics
    if inputs.get("critical") == "yes":
        score += 12
        factors.append(ScoreFactor("Special Characteristics (SC)", 12, 12))

    # 6) Customer bonus
    cb = int(inputs.get("customer_bonus") or 0)
    if cb > 0:
        score += cb
        factors.append(ScoreFactor(f"Customer ({inputs.get('customer_name','')})", cb, 10))

    # 7) KSK production system
    if inputs.get("prod_system") == "ksk":
        score += 6
        factors.append(ScoreFactor("KSK Production System", 6, 6))

    score = min(score, 100)
    return ScoreResult(score=score, factors=factors, **_classify(score))

def score_business_transfer(inputs: dict) -> ScoreResult:
    """
    Scores a Business Transfer based on Concept Checklist (8 risk areas)
    and Execution Checklist (31 steps) per EAGP procedures.

    Expected input keys:
        recv_plant_status : "mature" | "intermediate" | "new"
        eq_transfer_type  : "transfer" | "duplicate" | "new"
        design_freeze     : "yes" | "no"
        current_my        : "yes" | "no"
        safety_stock      : "yes" | "no"
        process_match     : "same" | "similar" | "different"
        source_claims     : "none" | "low" | "medium" | "high"
        pfmea             : int 1–10
        volume            : int
        critical          : "yes" | "no"
        prod_system       : "batch" | "ksk"
        customer_bonus    : int
        customer_name     : str
    """
    factors: List[ScoreFactor] = []
    score = 0

    # 1) Receiving plant capability (Concept Checklist Section 8)
    recv_map = {"mature": 5, "intermediate": 12, "new": 22}
    rv = recv_map.get(inputs.get("recv_plant_status", "intermediate"), 12)
    score += rv
    factors.append(ScoreFactor("Receiving Plant Status", rv, 22))

    # 2) Equipment transfer type (Section 5)
    eq_map = {"transfer": 5, "duplicate": 12, "new": 18}
    ev = eq_map.get(inputs.get("eq_transfer_type", "transfer"), 10)
    score += ev
    factors.append(ScoreFactor("Equipment Transfer Type", ev, 18))

    # 3) Active design changes during transfer (Section 4)
    if inputs.get("design_freeze") == "no":
        score += 12
        factors.append(ScoreFactor("Active Design Changes", 12, 12))

    # 4) Same Model Year (no ramp margin)
    if inputs.get("current_my") == "yes":
        score += 8
        factors.append(ScoreFactor("Same MY Transfer", 8, 8))

    # 5) No safety stock
    if inputs.get("safety_stock") == "no":
        score += 10
        factors.append(ScoreFactor("No Safety Stock Built", 10, 10))

    # 6) Process mismatch (Sections 8g / 8h)
    pm_map = {"same": 0, "similar": 6, "different": 12}
    pm = pm_map.get(inputs.get("process_match", "same"), 0)
    if pm > 0:
        score += pm
        factors.append(ScoreFactor("Process Mismatch", pm, 12))

    # 6b) Open claims at source plant — these travel with the product
    claims_map = {"none": 0, "low": 6, "medium": 14, "high": 22}
    cl = claims_map.get(inputs.get("source_claims", "none"), 0)
    if cl > 0:
        score += cl
        factors.append(ScoreFactor("Open Claims at Source", cl, 22))

    # 7) PFMEA Severity (Execution Step 14)
    pfmea = int(inputs.get("pfmea") or 5)
    pf = 15 if pfmea >= 9 else (10 if pfmea >= 7 else (6 if pfmea >= 5 else 3))
    score += pf
    factors.append(ScoreFactor(f"PFMEA Severity ({pfmea})", pf, 15))

    # 8) Volume
    vol = int(inputs.get("volume") or 0)
    vs = 8 if vol > 5000 else (5 if vol > 1000 else 2)
    score += vs
    factors.append(ScoreFactor("Volume / Day", vs, 8))

    # 9) Special Characteristics (SC) applied
    if inputs.get("critical") == "yes":
        score += 8
        factors.append(ScoreFactor("Special Characteristics (SC)", 8, 8))

    # 10) Customer
    cb = int(inputs.get("customer_bonus") or 0)
    if cb > 0:
        score += cb
        factors.append(ScoreFactor(f"Customer ({inputs.get('customer_name','')})", cb, 10))

    # 11) KSK
    if inputs.get("prod_system") == "ksk":
        score += 5
        factors.append(ScoreFactor("KSK Production System", 5, 5))

    score = min(score, 100)
    cls = _classify(score)

    # PRA forecast (per EAGP_4-4_CS_01)
    # Conformance % is inversely related to risk score
    conformance = 100 - score
    pra = "GREEN" if conformance >= 92 else ("YELLOW" if conformance >= 82 else "RED")

    return ScoreResult(
        score=score, factors=factors,
        pra_forecast=pra, conformance=conformance,
        **cls,
    )


# ═════════════════════════════════════════════════════════════════════════════
# 3. MY CHANGE / ENGINEERING CHANGE  (per EAEP_4-1_ME-EDS_10-01)
# ═════════════════════════════════════════════════════════════════════════════

def score_engineering_change(inputs: dict) -> ScoreResult:
    """
    Scores an Engineering / MY Change based on ECCL flow and feasibility.

    Expected input keys:
        feasibility_status : "approved" | "pending" | "rejected"
        eccl_stage         : "preliminary" | "interim" | "final" | "none"
        eo_costs           : "low" | "medium" | "high"
        change_type        : "my" | "design" | "material" | "process"
        multi_plant        : "yes" | "no"
        ksk_impact         : "yes" | "no"
        pfmea              : int
        volume             : int
        critical           : "yes" | "no"
        customer_bonus     : int
        customer_name      : str
    """
    factors: List[ScoreFactor] = []
    score = 0

    # 1) Feasibility study (Step 3 — single NO = not feasible = stop)
    feas_map = {"approved": 0, "pending": 8, "rejected": 25}
    fs = feas_map.get(inputs.get("feasibility_status", "pending"), 8)
    if fs > 0:
        score += fs
        factors.append(ScoreFactor("Feasibility Status", fs, 25))

    # 2) ECCL stage progress (Steps 7–9, 17)
    eccl_map = {"final": 0, "interim": 4, "preliminary": 8, "none": 15}
    es = eccl_map.get(inputs.get("eccl_stage", "preliminary"), 8)
    if es > 0:
        score += es
        factors.append(ScoreFactor("ECCL Stage", es, 15))

    # 3) E&O cost level (Step 13 — escalation thresholds 5k€ / 50k€)
    eo_map = {"low": 2, "medium": 8, "high": 15}
    eo = eo_map.get(inputs.get("eo_costs", "medium"), 8)
    score += eo
    factors.append(ScoreFactor("E&O Cost Level", eo, 15))

    # 4) Change type complexity
    ct_map = {"my": 12, "design": 10, "material": 8, "process": 6}
    ct = ct_map.get(inputs.get("change_type", "design"), 8)
    score += ct
    factors.append(ScoreFactor("Change Type Complexity", ct, 12))

    # 5) Multi-plant coordination (Step 4a/4b — Liaison Coordinator)
    if inputs.get("multi_plant") == "yes":
        score += 10
        factors.append(ScoreFactor("Multi-plant Coordination", 10, 10))

    # 6) KSK modules affected (Annex A01 — PB2O Update needed)
    if inputs.get("ksk_impact") == "yes":
        score += 8
        factors.append(ScoreFactor("KSK / PB2O Impact", 8, 8))

    # 7–9) PFMEA, Volume, Critical, Customer
    pfmea = int(inputs.get("pfmea") or 5)
    pf = 10 if pfmea >= 9 else (6 if pfmea >= 7 else (3 if pfmea >= 5 else 1))
    score += pf
    factors.append(ScoreFactor(f"PFMEA Severity ({pfmea})", pf, 10))

    vol = int(inputs.get("volume") or 0)
    vs = 6 if vol > 5000 else (4 if vol > 1000 else 2)
    score += vs
    factors.append(ScoreFactor("Volume / Day", vs, 6))

    if inputs.get("critical") == "yes":
        score += 8
        factors.append(ScoreFactor("Special Characteristics (SC)", 8, 8))

    cb = int(inputs.get("customer_bonus") or 0)
    if cb > 0:
        score += cb
        factors.append(ScoreFactor(f"Customer ({inputs.get('customer_name','')})", cb, 10))

    score = min(score, 100)
    return ScoreResult(score=score, factors=factors, **_classify(score))


# ═════════════════════════════════════════════════════════════════════════════
# 4. RESTART AFTER SHUTDOWN  (per HOGP_5-1_MG-EDS_01-F01)
# ═════════════════════════════════════════════════════════════════════════════

def score_restart(inputs: dict) -> ScoreResult:
    """
    Scores a Restart After Shutdown based on duration, type, prep quality.

    Expected input keys:
        shutdown_duration  : "short" | "medium" | "long"
        shutdown_type      : "planned" | "forced" | "emergency"
        prep_status        : "complete" | "partial" | "missing"
        contingency_team   : "yes" | "no"
        lpa_coverage       : "planned" | "partial" | "none"
        absenteeism_risk   : "low" | "medium" | "high"
        prod_system        : "batch" | "ksk"
        customer_bonus     : int
        customer_name      : str
    """
    factors: List[ScoreFactor] = []
    score = 0

    dur_map  = {"short": 5,  "medium": 12, "long": 20}
    type_map = {"planned": 3, "forced": 12, "emergency": 20}
    prep_map = {"complete": 0, "partial": 10, "missing": 18}
    lpa_map  = {"planned": 0, "partial": 6, "none": 12}
    abs_map  = {"low": 2, "medium": 8, "high": 15}

    d = dur_map.get(inputs.get("shutdown_duration", "medium"), 12)
    score += d
    factors.append(ScoreFactor("Shutdown Duration", d, 20))

    t = type_map.get(inputs.get("shutdown_type", "planned"), 12)
    score += t
    factors.append(ScoreFactor("Shutdown Type", t, 20))

    p = prep_map.get(inputs.get("prep_status", "partial"), 10)
    if p > 0:
        score += p
        factors.append(ScoreFactor("Shutdown Prep Gap", p, 18))

    if inputs.get("contingency_team") == "no":
        score += 8
        factors.append(ScoreFactor("No Contingency Response Team", 8, 8))

    l = lpa_map.get(inputs.get("lpa_coverage", "planned"), 6)
    if l > 0:
        score += l
        factors.append(ScoreFactor("LPA Coverage Gap", l, 12))

    a = abs_map.get(inputs.get("absenteeism_risk", "low"), 8)
    score += a
    factors.append(ScoreFactor("Absenteeism Risk", a, 15))

    # KSK requires more cleaning — higher restart complexity
    if inputs.get("prod_system") == "ksk":
        score += 6
        factors.append(ScoreFactor("KSK Cleanup Complexity", 6, 6))

    cb = int(inputs.get("customer_bonus") or 0)
    if cb > 0:
        # For restart, customer risk is partial (not full supply chain risk)
        cb_adj = round(cb * 0.6)
        score += cb_adj
        factors.append(ScoreFactor(f"Customer ({inputs.get('customer_name','')})", cb_adj, 10))

    score = min(score, 100)
    return ScoreResult(score=score, factors=factors, **_classify(score))


# ═════════════════════════════════════════════════════════════════════════════
# 5. ABSENCE / TURNOVER  (Workforce Stability Program)
# ═════════════════════════════════════════════════════════════════════════════

def score_absence(inputs: dict) -> ScoreResult:
    """
    Scores an Absence / Turnover situation based on headcount gap and turnover %.

    Expected input keys:
        hc_current    : int — current headcount
        hc_affected   : int — number of positions affected
        turnover_pct  : float — annualised turnover %
        experience    : "low" | "high"
        volume        : int
        critical      : "yes" | "no"
        customer_bonus: int
        customer_name : str
    """
    factors: List[ScoreFactor] = []
    score = 0

    hc_current  = int(inputs.get("hc_current")  or 0)
    hc_affected = int(inputs.get("hc_affected") or 0)
    turnover    = float(inputs.get("turnover_pct") or 0)

    # Headcount gap % — derived, not directly input
    # max(1, x) prevents division by zero
    gap_pct = (hc_affected / max(1, hc_current)) * 100

    gap_score = (30 if gap_pct >= 30 else
                 22 if gap_pct >= 15 else
                 12 if gap_pct >= 5  else 5)
    score += gap_score
    factors.append(ScoreFactor(f"Headcount Gap ({gap_pct:.0f}%)", gap_score, 30))

    tr_score = (22 if turnover >= 25 else
                14 if turnover >= 15 else
                6  if turnover >= 5  else 2)
    score += tr_score
    factors.append(ScoreFactor(f"Turnover Rate ({turnover:.0f}%)", tr_score, 22))

    if inputs.get("experience") == "low":
        score += 18
        factors.append(ScoreFactor("Low Team Experience", 18, 18))

    vol = int(inputs.get("volume") or 0)
    vs = 12 if vol > 5000 else (7 if vol > 1000 else 3)
    score += vs
    factors.append(ScoreFactor("Volume Impacted", vs, 12))

    if inputs.get("critical") == "yes":
        score += 12
        factors.append(ScoreFactor("Special Characteristics (SC)", 12, 12))

    cb = int(inputs.get("customer_bonus") or 0)
    if cb > 0:
        cb_adj = round(cb * 0.6)
        score += cb_adj
        factors.append(ScoreFactor(f"Customer ({inputs.get('customer_name','')})", cb_adj, 10))

    score = min(score, 100)
    return ScoreResult(score=score, factors=factors, **_classify(score))


# ═════════════════════════════════════════════════════════════════════════════
# 6. CAPACITY CHANGE  (per EAGP_5-3_ME_02)
# ═════════════════════════════════════════════════════════════════════════════

def score_capacity(inputs: dict) -> ScoreResult:
    """
    Scores a Capacity Change based on demand delta, ATV, and action plan.

    Expected input keys:
        volume_current : int (pcs/day now)
        volume_new     : int (pcs/day target)
        atv_status     : "approved" | "pending" | "missing"
        sys_flow_change: "yes" | "no"   (triggers PFMEA if yes)
        capacity_action: "overtime" | "banking" | "duplicate" | "newline"
        ruc_defined    : "yes" | "no"
        area_change    : "yes" | "no"
        pfmea          : int
        critical       : "yes" | "no"   (Special Characteristics applied)
        prod_system    : "batch" | "ksk"
        customer_bonus : int
        customer_name  : str
    """
    factors: List[ScoreFactor] = []
    score = 0

    # Auto-compute demand delta % from volumes
    v_cur = int(inputs.get("volume_current") or 0)
    v_new = int(inputs.get("volume_new") or 0)

    if v_cur > 0 and v_new > 0:
        # f-string formatting: :.0f means 0 decimal places
        delta_pct = (v_new - v_cur) / v_cur * 100
        demand_bucket = (
            "large"    if delta_pct >= 50 else
            "medium"   if delta_pct >= 25 else
            "small"    if delta_pct >= 0  else
            "decrease"
        )
    else:
        delta_pct = 0
        demand_bucket = "small"

    demand_map = {"decrease": 5, "small": 8, "medium": 14, "large": 22}
    ds = demand_map[demand_bucket]
    score += ds
    factors.append(ScoreFactor(f"Demand Change ({delta_pct:+.0f}%)", ds, 22))

    atv_map = {"approved": 0, "pending": 6, "missing": 12}
    av = atv_map.get(inputs.get("atv_status", "pending"), 6)
    if av > 0:
        score += av
        factors.append(ScoreFactor("ATV Approval Status", av, 12))

    if inputs.get("sys_flow_change") == "yes":
        score += 14
        factors.append(ScoreFactor("MFG Flow Change (PFMEA req.)", 14, 14))

    act_map = {"overtime": 3, "banking": 5, "duplicate": 12, "newline": 18}
    ac = act_map.get(inputs.get("capacity_action", "overtime"), 5)
    score += ac
    factors.append(ScoreFactor("Capacity Action Complexity", ac, 18))

    if inputs.get("ruc_defined") == "no":
        score += 10
        factors.append(ScoreFactor("No Ramp-Up Curve Defined", 10, 10))

    if inputs.get("area_change") == "yes":
        score += 8
        factors.append(ScoreFactor("Production Area Change", 8, 8))

    pfmea = int(inputs.get("pfmea") or 5)
    pf = 10 if pfmea >= 9 else (6 if pfmea >= 7 else (3 if pfmea >= 5 else 1))
    score += pf
    factors.append(ScoreFactor(f"PFMEA Severity ({pfmea})", pf, 10))

    if inputs.get("critical") == "yes":
        score += 8
        factors.append(ScoreFactor("Special Characteristics (SC)", 8, 8))

    if inputs.get("prod_system") == "ksk":
        score += 5
        factors.append(ScoreFactor("KSK Production System", 5, 5))

    cb = int(inputs.get("customer_bonus") or 0)
    if cb > 0:
        score += cb
        factors.append(ScoreFactor(f"Customer ({inputs.get('customer_name','')})", cb, 10))

    score = min(score, 100)
    return ScoreResult(score=score, factors=factors, **_classify(score))


# ═════════════════════════════════════════════════════════════════════════════
# 7. NEW PLANT LAUNCH
# Source: Aptiv New Plant Flawless Launch Support Initiative (Apr 2025)
#         + RASIC table (Critical Processes Assessment, PRA, GP12, PPAP...)
# ═════════════════════════════════════════════════════════════════════════════

def score_new_plant(inputs: dict) -> ScoreResult:
    """
    Scores a New Plant Launch based on the Aptiv Flawless Launch Initiative.

    Covers 4 gap categories from the initiative:
      - People (team seniority, mother plant, new hires)
      - Process (Quality Master Plan, PPAP, PFMEA, mother issues)
      - Infrastructure Readiness (IT tools, green field, plant type)
      - Customer (SC, volume, PPAP plan with R@R)

    Expected input keys:
        plant_type             : "greenfield" | "brownfield"
        mother_plant           : "yes" | "no"
        it_readiness           : "ready" | "partial" | "not_started"
        team_seniority         : "experienced" | "mixed" | "new"
        qmp_done               : "yes" | "partial" | "no"
        green_field_assess     : "yes" | "no"
        mother_issues_received : "yes" | "no"
        ppap_plan_ready        : "yes" | "no"
        pfmea                  : int 1–10
        headcount              : int
        volume                 : int (pcs/day)
        critical               : "yes" | "no"  (Special Characteristics)
        customer_bonus         : int
        customer_name          : str
    """
    factors: List[ScoreFactor] = []
    score = 0

    # ── PEOPLE (gap category 1) ───────────────────────────────────────────
    # Team seniority / capabilities — most critical people gap
    seniority_map = {"experienced": 0, "mixed": 12, "new": 22}
    sen = seniority_map.get(inputs.get("team_seniority", "mixed"), 12)
    if sen > 0:
        score += sen
        factors.append(ScoreFactor("Team Seniority / Capabilities", sen, 22))

    # Mother plant not identified — key gap from initiative
    if inputs.get("mother_plant") == "no":
        score += 16
        factors.append(ScoreFactor("Mother Plant Not Identified", 16, 16))

    # Headcount sizing
    hc = int(inputs.get("headcount") or 0)
    if hc > 0:
        hc_score = 10 if hc > 40 else (6 if hc > 20 else 3)
        score += hc_score
        factors.append(ScoreFactor(f"Quality Team Headcount ({hc})", hc_score, 10))

    # ── PROCESS (gap category 2) ──────────────────────────────────────────
    # Quality Master Plan not reviewed — no standard QMP = critical gap
    qmp_map = {"yes": 0, "partial": 8, "no": 18}
    qmp = qmp_map.get(inputs.get("qmp_done", "partial"), 8)
    if qmp > 0:
        score += qmp
        factors.append(ScoreFactor("Quality Master Plan Not Reviewed", qmp, 18))

    # Historic quality issues from mother plant
    if inputs.get("mother_issues_received") == "no":
        score += 12
        factors.append(ScoreFactor("No Quality History from Mother Plant", 12, 12))

    # PPAP plan not defined (incl. R@R requirements)
    if inputs.get("ppap_plan_ready") == "no":
        score += 10
        factors.append(ScoreFactor("PPAP Plan Not Defined (incl. R@R)", 10, 10))

    # PFMEA severity
    pfmea = int(inputs.get("pfmea") or 5)
    pf = 16 if pfmea >= 9 else (12 if pfmea >= 7 else (7 if pfmea >= 5 else 3))
    score += pf
    factors.append(ScoreFactor(f"PFMEA Severity ({pfmea})", pf, 16))

    # ── INFRASTRUCTURE READINESS (gap category 3) ─────────────────────────
    # Green field — highest infrastructure risk
    if inputs.get("plant_type") == "greenfield":
        score += 14
        factors.append(ScoreFactor("Green Field Site (no automotive history)", 14, 14))

    # Green field assessment not performed
    if inputs.get("green_field_assess") == "no":
        score += 10
        factors.append(ScoreFactor("Green Field Assessment Not Performed", 10, 10))

    # IT tools readiness (SAP, DCiX, CAO, APRISO, ALS, PFT, QAuditor)
    it_map = {"ready": 0, "partial": 8, "not_started": 18}
    it = it_map.get(inputs.get("it_readiness", "partial"), 8)
    if it > 0:
        score += it
        factors.append(ScoreFactor("IT Tools Not Ready (SAP/DCiX/CAO...)", it, 18))

    # ── CUSTOMER (gap category 4) ─────────────────────────────────────────
    # Special Characteristics
    if inputs.get("critical") == "yes":
        score += 12
        factors.append(ScoreFactor("Special Characteristics (SC)", 12, 12))

    # Volume
    vol = int(inputs.get("volume") or 0)
    vs = 10 if vol > 3000 else (6 if vol > 1000 else 3)
    score += vs
    factors.append(ScoreFactor("Volume / Day", vs, 10))

    # Customer bonus — skip if "default" (no customer confirmed yet)
    customer = inputs.get("customer", "other")
    cb = int(inputs.get("customer_bonus") or 0)
    if cb > 0 and customer != "default":
        score += cb
        factors.append(ScoreFactor(f"Customer ({inputs.get('customer_name','')})", cb, 10))

    score = min(score, 100)
    cls = _classify(score)

    # New Plant: continuous monitoring — no fixed safe launch window
    cls["duration"] = 0                          # 0 = not applicable / continuous
    cls["fpy"]      = "Per GP12 exit criteria"

    # Replace standard recommendation with new plant specific message
    cls["recommendation"] = (
        "New Plant requires continuous quality monitoring — no fixed safe launch exit date. "
        "Activate GP12 containment at SOP. "
        "Ensure expert support team from sister plant present from Process Release to 4 weeks after SOP. "
        "Complete Green Field Assessment before SOP. "
        "Confirm mother plant quality history received 8 weeks before SOP. "
        "Validate IT tools (SAP / DCiX / CAO / APRISO) operational 4 weeks before SOP. "
        "Exit GP12 only on customer formal confirmation — not on a fixed timeline."
    )

    return ScoreResult(score=score, factors=factors, **cls)


# ═════════════════════════════════════════════════════════════════════════════
# DISPATCHER — one entry point for all program types
# ═════════════════════════════════════════════════════════════════════════════

# Maps program type string → the correct function
# This is a "function lookup table" — avoids a long if/elif chain
SCORE_FUNCTIONS = {
    "new":       score_new_program,
    "new_plant": score_new_plant,
    "transfer":  score_business_transfer,
    "my_change": score_engineering_change,
    "restart":   score_restart,
    "absence":   score_absence,
    "capacity":  score_capacity,
}


def calculate_score(program_type: str, inputs: dict) -> ScoreResult:
    """
    Main entry point. Call this from the UI.

    Example:
        result = calculate_score("restart", {"shutdown_duration": "long", ...})
        print(result.score)    # 72
        print(result.risk)     # "HIGH"
    """
    # dict.get(key) returns None if key not found
    fn = SCORE_FUNCTIONS.get(program_type)
    if fn is None:
        # raise = throw an error and stop — ValueError = wrong value passed
        raise ValueError(f"Unknown program type: '{program_type}'. "
                         f"Valid types: {list(SCORE_FUNCTIONS.keys())}")
    return fn(inputs)
