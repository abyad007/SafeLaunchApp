# core/checklist_loader.py
# ─────────────────────────────────────────────────────────────────────────────
# Generates quality-focused safe launch checklists per program type.
#
# Design principle:
#   - NO file extraction from procedure documents (too noisy, too much duplication)
#   - All checklists are hand-curated quality action items
#   - Organized into 4 quality domains per Versigent MO2 standard:
#       Quality Structure | Customer Requirements | Quality Readiness | Quality Confirmation
#   - Context-aware: items adapt based on customer, production system, risk level
#   - Customer-specific items (VW/Renault/Stellantis/Mercedes) injected automatically
# ─────────────────────────────────────────────────────────────────────────────

from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data" / "procedures"


@dataclass
class ChecklistItem:
    """One quality action item in a safe launch checklist."""
    step:     str
    text:     str
    phase:    str  = ""      # quality domain: Structure / Requirements / Readiness / Confirmation
    critical: bool = False
    warn:     bool = False
    done:     bool = False


# ═════════════════════════════════════════════════════════════════════════════
# QUALITY CHECKLISTS — per program type
# Source: Versigent MO2 Quality Performance Review standard
# ═════════════════════════════════════════════════════════════════════════════

# ── Shared quality domains used across programs ───────────────────────────

_QUALITY_STRUCTURE_BASE = [
    ("QS-1", "Define quality team members and assign roles (IH / DH)"),
    ("QS-2", "Confirm quality leader accountability and escalation path"),
    ("QS-3", "Establish quality communication cadence with plant management"),
]

_QUALITY_STRUCTURE_NEW = [
    ("QS-1", "Define VW IS quality team members and assign responsibilities"),
    ("QS-2", "Define quality IH and DH structure for the program"),
    ("QS-3", "Confirm BIQ Leader is assigned and onboarded to the project"),
    ("QS-4", "Establish quality escalation matrix and communication cadence"),
]

_QUALITY_CONFIRMATION_BASE = [
    ("QC-1", "Train quality inspectors on drawing, specification and critical characteristics"),
    ("QC-2", "Implement 100% EOL quality containment and firewall at SOP"),
    ("QC-3", "Validate final product 100% against approved drawing during ramp-up curve"),
    ("QC-4", "Increase teardown frequency to minimum 1 piece per month during safe launch"),
    ("QC-5", "Establish hourly, daily and weekly VOP / QIP Gemba review cadence"),
    ("QC-6", "Assign dedicated quality expert monitoring during RC (Ramp-up Confirmation)"),
    ("QC-7", "Activate First Time Quality (FTQ) monitoring dashboard — track daily KPIs"),
]


# ═════════════════════════════════════════════════════════════════════════════
# 1. NEW PROGRAM — per EANP_4-1_CS_01-03 + MO2 Quality Standard
# ═════════════════════════════════════════════════════════════════════════════

_NEW_PROGRAM: List[Tuple] = [
    # ── Quality Structure ─────────────────────────────────────────────────
    ("QS-1", "Define quality team structure — assign quality lead and plant quality manager",     "Quality Structure", False),
    ("QS-2", "Confirm team experience level — identify gaps and plan bridging training",          "Quality Structure", False),
    ("QS-3", "Define operator training plan — headcount, skills certification and timeline",      "Quality Structure", False),
    ("QS-4", "Establish quality escalation matrix and management review cadence",                 "Quality Structure", False),
    ("QS-5", "Assess team / customer experience — plan gap-filling actions accordingly",          "Quality Structure", False),

    # ── Customer Requirements ──────────────────────────────────────────────
    ("CR-1", "Identify and document all Customer Specific Requirements (CSR)",                    "Customer Requirements", True),
    ("CR-2", "Confirm customer portal access — complete required customer trainings",             "Customer Requirements", False),
    ("CR-3", "Align quality deliverables with customer launch timing and gate requirements",      "Customer Requirements", True),
    ("CR-4", "Define Special Characteristics (SC) — validate measurement capability for each",   "Customer Requirements", True),
    ("CR-5", "Obtain customer approval for Production Trial Run (PTR) before SOP",               "Customer Requirements", True),

    # ── Quality Readiness ─────────────────────────────────────────────────
    ("QR-1",  "Complete DFMEA — close all high-risk actions before process validation",          "Quality Readiness", True),
    ("QR-2",  "Complete PFMEA — focus on critical characteristics and high severity failures",   "Quality Readiness", True),
    ("QR-3",  "Develop Process Control Plan from PFMEA and customer requirements",               "Quality Readiness", True),
    ("QR-4",  "Complete MSA (Gauge R&R) for all Special Characteristics measurements",           "Quality Readiness", True),
    ("QR-5",  "Confirm process capability (Cp/Cpk) for all critical characteristics",            "Quality Readiness", True),
    ("QR-6",  "Perform line process release — readiness audit approved by Plant Quality",        "Quality Readiness", True),
    ("QR-7",  "Define and document Safe Launch Plan — exit criteria clearly stated",             "Quality Readiness", True),
    ("QR-8",  "Submit full PPAP package — obtain customer approval before SOP",                  "Quality Readiness", True),
    ("QR-9",  "Validate Error-Proofing / Poka-Yoke devices at all critical stations",           "Quality Readiness", False),
    ("QR-10", "Gather lessons learned from similar programs — integrate into launch plan",       "Quality Readiness", False),
    ("QR-11", "Build prototype / pilot parts — validate against approved drawing",               "Quality Readiness", False),
    ("QR-12", "Confirm full PPAP approval — zero open quality issues before SOP",               "Quality Readiness", True),

    # ── Quality Confirmation ──────────────────────────────────────────────
    ("QC-1", "Train quality inspectors on drawing, specification and critical characteristics",  "Quality Confirmation", False),
    ("QC-2", "Implement 100% control at all SC-related stations",                               "Quality Confirmation", True),
    ("QC-3", "Activate 100% EOL quality containment and firewall",                              "Quality Confirmation", True),
    ("QC-4", "Validate final product 100% against approved drawing during ramp-up curve",       "Quality Confirmation", True),
    ("QC-5", "Increase teardown frequency — minimum 1 piece per month during safe launch",      "Quality Confirmation", False),
    ("QC-6", "Establish hourly, daily and weekly VOP / QIP Gemba review cadence",              "Quality Confirmation", False),
    ("QC-7", "Assign dedicated quality expert monitoring during RC (Ramp-up Confirmation)",     "Quality Confirmation", False),
    ("QC-8", "Activate First Time Quality (FTQ) monitoring dashboard — track daily KPIs",                  "Quality Confirmation", False),
    ("QC-9", "Hand over program to Plant Quality — document lessons learned for future programs","Quality Confirmation", False),
]



# ═════════════════════════════════════════════════════════════════════════════
# 2. BUSINESS TRANSFER — per EAGP_4-4_MG_01 + MO2 Quality Standard
# ═════════════════════════════════════════════════════════════════════════════

_BUSINESS_TRANSFER: List[Tuple] = [
    # ── Quality Structure ─────────────────────────────────────────────────
    # Source: EAGP_4-4_MG_01_EN.pptx — Management Process
    ("QS-1",  "Assign Business Transfer Manager — define accountability and escalation path",             "Quality Structure", False),
    ("QS-2",  "Assign Transfer Team members from both Transferring and Receiving plants",                 "Quality Structure", False),
    ("QS-3",  "Define quality lead at Receiving Plant — confirm IH/DH structure",                        "Quality Structure", False),
    ("QS-4",  "Establish management review cadence — schedule at minimum one review with BU/Operations Director", "Quality Structure", False),

    # ── Customer Requirements ──────────────────────────────────────────────
    # Source: EAGP_4-4_MG_01-F01_EN.xlsx steps 1, 2, 3, 6, 12, 16, 18
    ("CR-1",  "Receive Customer Notification and Conditions to execute the transfer",                     "Customer Requirements", True),
    ("CR-2",  "Notify Sales Department for Customer Contract change",                                     "Customer Requirements", False),
    ("CR-3",  "Verify IGS/FSS Contract is fixed and signed if applicable",                               "Customer Requirements", False),
    ("CR-4",  "Review Customer and Tier 1 Expectations and Requirements (CSI, SQAM, GPs)",               "Customer Requirements", True),
    ("CR-5",  "Get information from Customer related to schedules and volumes during transfer period",    "Customer Requirements", True),
    ("CR-6",  "Identify Customer key contacts at VAP, SQE, CSE, and Aptiv warehouses / SILS",           "Customer Requirements", False),
    ("CR-7",  "Get Customer approval for PTR (Production Trial Run) Plan — quantities, timing, conditions", "Customer Requirements", True),

    # ── Quality Readiness ─────────────────────────────────────────────────
    # Source: EAGP_4-4_MG_01-F01_EN.xlsx steps 4, 5, 7–15, 17–27
    # Source: EAGP_2-6_BU_02-F01_EN.xlsm — Concept Checklist risk items
    ("QR-1",  "Define Project Timing Plan — include all transfer milestones and customer gates",          "Quality Readiness", False),
    ("QR-2",  "Develop Capacity Study: define Start-Up Plan, Ramp-Up Curve and Safety Stock levels",     "Quality Readiness", True),
    ("QR-3",  "Check inventory and E&O risk at origin plant and SILS/warehouses",                        "Quality Readiness", False),
    ("QR-4",  "Identify potential Engineering Changes that may occur during the transfer period",         "Quality Readiness", True),
    ("QR-5",  "Analyze harnesses produced by Transferring Plant vs. drawings and BOMs",                  "Quality Readiness", True),
    # Step 13 — Equipment & tooling
    ("QR-6",  "Calibrate all required equipment per Aptiv and Customer Standards",                       "Quality Readiness", True),
    ("QR-7",  "Assure Tooling, Process Equipment and Rework tooling release per Aptiv and Customer standards", "Quality Readiness", True),
    ("QR-8",  "Implement Statistical Process Control (SPC) to evaluate process capability at Receiving Plant", "Quality Readiness", True),
    ("QR-9",  "Research export laws and requirements from origin to destination country",                 "Quality Readiness", False),
    # Step 14 — Process Control
    ("QR-10", "Review Process Flow Diagram (PFD) between Transferring and Receiving plants",              "Quality Readiness", True),
    ("QR-11", "Analyze PFMEA between both plants with multidisciplinary team — align control plan",       "Quality Readiness", True),
    ("QR-12", "Identify KPC / KCC / CCS designated by Customer and verify preventive/detection actions", "Quality Readiness", True),
    ("QR-13", "Analyze Customer Complaints and respective Corrective Actions — confirm closure before SOP", "Quality Readiness", True),
    ("QR-14", "Ensure Special Characteristics are included in Control Plan and Working Methods",          "Quality Readiness", True),
    ("QR-15", "Identify and define inspection checkpoints, frequency and sampling plan at Receiving Plant", "Quality Readiness", True),
    # Step 15 — Quality History
    ("QR-16", "Analyze FTQ, Red Tags and Supplier performance at origin plant",                          "Quality Readiness", True),
    ("QR-17", "Transfer Quality Records to Receiving Plant — identify lessons learned and best practices", "Quality Readiness", False),
    ("QR-18", "Analyze Customer Feedback records since Project SOP at origin plant",                      "Quality Readiness", True),
    # Step 17 — New Hiring
    ("QR-19", "Identify training needs for all personnel involved at Receiving Plant",                    "Quality Readiness", False),
    ("QR-20", "Ensure awareness training on key, safety and regulatory characteristics",                  "Quality Readiness", True),
    ("QR-21", "Complete Customer-specific Requirements acceptance/rejection criteria training",            "Quality Readiness", True),
    ("QR-22", "Certify operators at key and critical stations — generate Flexibility Chart / Skills Matrix", "Quality Readiness", True),
    # Steps 19–27 — Operational readiness
    ("QR-23", "Activate DUNS Code — implement Current and Future MY Part Numbers at Receiving Plant",    "Quality Readiness", False),
    ("QR-24", "Verify purchased component Material Master SAP data is created at Receiving Plant",        "Quality Readiness", False),
    ("QR-25", "Verify purchased component Material PPAP is approved for new supplier if applicable",      "Quality Readiness", True),
    ("QR-26", "Transfer ePPAP/PPAP files to Receiving Plant per EAGP_4-4_MG_01-F01 Step 21",            "Quality Readiness", True),
    ("QR-27", "Get Customer approval for packaging if different from Transferring Plant",                 "Quality Readiness", False),
    ("QR-28", "Verify IT systems and data links are updated to reflect the Receiving Plant",              "Quality Readiness", False),
    ("QR-29", "Obtain environmental, health and safety permits at Receiving Plant before SOP",            "Quality Readiness", False),
    # Concept Checklist risks — EAGP_2-6_BU_02-F01_EN
    ("QR-30", "Assess risk: receiving plant experience level — confirm sufficient skilled resources and manufacturing floorspace", "Quality Readiness", True),
    ("QR-31", "Assess risk: manufacturing processes and working practices are common between plants — document gaps", "Quality Readiness", True),
    ("QR-1b", "Review and formally close all open customer claims at source plant before transfer SOP",  "Quality Readiness", True),
    ("QR-1c", "Transfer all open claim documentation and 8D files to Receiving Plant quality team",      "Quality Readiness", True),

    # ── Quality Confirmation ──────────────────────────────────────────────
    # Source: EAGP_4-4_MG_01_EN.pptx + EAGP_4-4_CS_01 PRA process
    # Steps 28–31 are the mandatory closing gates
    ("QC-1",  "Get BMG (Build Master Gate) approval if applicable — Volkswagen programs mandatory",       "Quality Confirmation", True),
    ("QC-2",  "Get PPAP approval from OEM and Tier 1 customers for Receiving Plant",                     "Quality Confirmation", True),
    ("QC-3",  "Perform Internal Process Audit at Receiving Plant before SOP",                            "Quality Confirmation", True),
    ("QC-4",  "Perform Run @ Rate Audit at Receiving Plant",                                             "Quality Confirmation", True),
    # PRA — EAGP_4-4_CS_01 Production Readiness Assessment
    ("QC-5",  "Schedule and perform Production Readiness Assessment (PRA) — target GREEN (≥ 92%)",       "Quality Confirmation", True),
    ("QC-6",  "Define PRA Assessment Team Leader and Assessment Team before SOP − 8 weeks",              "Quality Confirmation", False),
    ("QC-7",  "Complete PRA action plan — all RED findings must have owner and closure date",             "Quality Confirmation", True),
    ("QC-8",  "Run Production Readiness Review as closing meeting of the PRA process",                   "Quality Confirmation", True),
    ("QC-9",  "Activate 100% EOL quality containment during transfer ramp-up period",                    "Quality Confirmation", True),
    ("QC-10", "Track daily FTQ and quality KPIs against Ramp-Up Curve — escalate if deviation",         "Quality Confirmation", True),
    ("QC-11", "Close Transfer — review metrics and confirm SOP at Receiving Plant achieved",              "Quality Confirmation", False),
]



# ═════════════════════════════════════════════════════════════════════════════
# 3. MY CHANGE / ENGINEERING CHANGE — per EAEP_4-1_ME-EDS_10-01
# ═════════════════════════════════════════════════════════════════════════════

_MY_CHANGE: List[Tuple] = [
    # ── Quality Structure ─────────────────────────────────────────────────
    # Source: EAEP_4-1_ME-EDS_10-01_EN.pptx — Swim Lanes / RASI
    ("QS-1", "Assign CIL (Change Implementation Leader) — confirm ME ownership for this change",          "Quality Structure", False),
    ("QS-2", "Confirm Customer Satisfaction authority for system/process release sign-off",               "Quality Structure", False),
    ("QS-3", "Identify Liaison Coordinator if same product is produced in more than one plant",           "Quality Structure", False),

    # ── Customer Requirements ──────────────────────────────────────────────
    # Source: EAEP_4-1_ME-EDS_10-01_EN.pptx — Steps 1, 2, 3, 6, 7
    ("CR-1", "Receive Change Request (CR) via ECM, email or SharePoint — log and acknowledge",            "Customer Requirements", False),
    ("CR-2", "Analyze the change with project team within customer-specified feasibility timing",          "Customer Requirements", True),
    ("CR-3", "Complete Feasibility Study — single NO response makes change not feasible (go to Step 21)", "Customer Requirements", True),
    ("CR-4", "Consolidate change cost and propose implementation date — include Labor, Material, Investment, E&O", "Customer Requirements", False),
    ("CR-5", "Receive Change Notice (CN) from customer via ECM, email or SharePoint",                     "Customer Requirements", True),
    ("CR-6", "Confirm PPAP submission level required for this engineering change",                        "Customer Requirements", True),

    # ── Quality Readiness ─────────────────────────────────────────────────
    # Source: EAEP_4-1_ME-EDS_10-01_EN.pptx — Steps 4a, 5, 8–14
    ("QR-1",  "If multi-plant: send information to Liaison Coordinator — align feedbacks between plants",  "Quality Readiness", False),
    ("QR-2",  "Submit Preliminary ECCL (or equivalent) with cost updates to CO/CL",                       "Quality Readiness", False),
    ("QR-3",  "Receive Change Notice (CN) and submit Preliminary ECCL with updates if CR vs CN delta",    "Quality Readiness", False),
    ("QR-4",  "Distribute Interim ECCL after CO/CL approval — only when ME receives approval",            "Quality Readiness", False),
    ("QR-5",  "Prepare ME internal documents (ECL or equivalent) and define Engineering Change Implementation Plan", "Quality Readiness", False),
    ("QR-6",  "Submit ECL for approval — minimum one step of control by ME project leader",               "Quality Readiness", False),
    ("QR-7",  "Conduct periodic follow-up of Engineering Change Implementation Plan during execution",     "Quality Readiness", False),
    ("QR-8",  "Coordinate E&O material identification and disposition — escalate per threshold (5k€/50k€)", "Quality Readiness", False),
    ("QR-9",  "Update PFMEA to reflect the change — reassess severity, occurrence and detection ratings", "Quality Readiness", True),
    ("QR-10", "Update Control Plan — confirm Special Characteristics are correctly identified if affected", "Quality Readiness", True),
    ("QR-11", "Confirm MSA validity for changed characteristics — re-run Gauge R&R if measurement system affected", "Quality Readiness", True),
    ("QR-12", "Update PB2O if change affects KSK modules — confirm alignment before implementation",       "Quality Readiness", False),

    # ── Quality Confirmation ──────────────────────────────────────────────
    # Source: EAEP_4-1_ME-EDS_10-01_EN.pptx — Steps 15, 16, 17, 18, 19
    ("QC-1", "Implement change and produce first part — verify 100% against customer-approved drawing",   "Quality Confirmation", True),
    ("QC-2", "Customer Satisfaction performs system/process release after first part validation",          "Quality Confirmation", True),
    ("QC-3", "Implement enhanced containment during changeover period — until process stability confirmed","Quality Confirmation", True),
    ("QC-4", "Distribute Final ECCL (or equivalent) within 2 weeks of implementation",                   "Quality Confirmation", False),
    ("QC-5", "Confirm packaging identification is updated if labelling or marking is affected by change",  "Quality Confirmation", False),
    ("QC-6", "Monitor FTQ daily for first 30 days post-implementation — root-cause any deviation",        "Quality Confirmation", True),
    ("QC-7", "If change not feasible: inform CO/CL with completed feasibility checklist justification (Step 21)", "Quality Confirmation", False),
]



# ═════════════════════════════════════════════════════════════════════════════
# 4. RESTART AFTER SHUTDOWN — per HOGP_5-1_MG-EDS_01-F01
# ═════════════════════════════════════════════════════════════════════════════

_RESTART: List[Tuple] = [
    # ── Quality Structure ─────────────────────────────────────────────────
    ("QS-1", "Confirm Contingency Response Team — define quality representative",              "Quality Structure",     True),
    ("QS-2", "Review and update Shutdown / Restart Risk Assessment (PFMEA)",                  "Quality Structure",     True),
    ("QS-3", "Define daily quality communication cadence for restart period",                 "Quality Structure",     False),
    ("QS-4", "Communicate contingency contact list to customer before shutdown",              "Quality Structure",     False),

    # ── Shutdown Preparation ───────────────────────────────────────────────
    ("SP-1", "Review Customer Requirements (portal notifications, open quality actions)",     "Shutdown Prep",         True),
    ("SP-2", "Ensure all NCR parts are stored in RED cage — documented and identified",      "Shutdown Prep",         True),
    ("SP-3", "Batch: pack splices & kits in lines | KSK: clean all WIP before shutdown",    "Shutdown Prep",         False),
    ("SP-4", "Protect dies, seal applicators — move to die center with correct storage",     "Shutdown Prep",         False),
    ("SP-5", "Verify PUR machine stoppage per supplier specifications and POS",              "Shutdown Prep",         False),
    ("SP-6", "Inform suppliers and logistics provider of shutdown plan and restart date",    "Shutdown Prep",         False),

    # ── Quality Readiness (Start-Up) ──────────────────────────────────────
    ("QR-1", "Verify IT systems (SAP, DCIX) operational before restart",                    "Quality Readiness",      True),
    ("QR-2", "Check critical supplier status — confirm components available for production", "Quality Readiness",     True),
    ("QR-3", "Verify RED cage content matches rejection list — resolve discrepancies",       "Quality Readiness",     True),
    ("QR-4", "Map operator presence day 1 — plan absenteeism coverage per shift",          "Quality Readiness",      True),
    ("QR-5", "Complete LPA (Layered Process Audit) in Incoming / Receiving area before release", "Quality Readiness", True),
    ("QR-6", "Retrieve and validate dies / seal applicators before Cutting & LP restart",  "Quality Readiness",      False),
    ("QR-7", "Verify first cuts against specification before releasing Cutting area",       "Quality Readiness",      True),
    ("QR-8", "Complete LPA in Cutting & LP area before release",                           "Quality Readiness",      True),
    ("QR-9", "Retrieve boards / kit boards from foil protection — inspect for damage",     "Quality Readiness",      False),
    ("QR-10","Produce first-off harness in FA area — validate against approved reference", "Quality Readiness",      True),
    ("QR-11","Validate EOL test station before releasing FA area to production",           "Quality Readiness",      True),
    ("QR-12","Complete LPA in FA area before release",                                    "Quality Readiness",       True),

    # ── Quality Confirmation ──────────────────────────────────────────────
    ("QC-1", "Activate enhanced FTQ monitoring — track daily output vs. quality targets",  "Quality Confirmation",   True),
    ("QC-2", "Hold daily stand-up: Production / Quality / HR on restart status",           "Quality Confirmation",   False),
    ("QC-3", "Track 1st-day and 1st-week quality incidents — root-cause by end of week 1","Quality Confirmation",   True),
    ("QC-4", "Review open supplier claims and sorting actions before accepting components", "Quality Confirmation",  False),
    ("QC-5", "Increase LPA frequency to daily during the first week of restart",          "Quality Confirmation",    True),
    ("QC-6", "Confirm ramp-up curve tracking — escalate if quantity or quality deviates", "Quality Confirmation",    True),
]


# ═════════════════════════════════════════════════════════════════════════════
# 5. ABSENCE / TURNOVER — Workforce Stability Program
# ═════════════════════════════════════════════════════════════════════════════

_ABSENCE: List[Tuple] = [
    # ── Quality Structure ─────────────────────────────────────────────────
    ("QS-1", "Map all affected positions — identify quality-critical roles at risk",            "Quality Structure",     True),
    ("QS-2", "Define backup operator structure per shift for each critical quality position",   "Quality Structure",     True),
    ("QS-3", "Assign quality lead accountable for safe launch monitoring during gap period",    "Quality Structure",     False),

    # ── Workforce Requirements ─────────────────────────────────────────────
    ("WF-1", "Schedule cross-training for backup operators on critical characteristics",        "Workforce Actions",     True),
    ("WF-2", "Verify operator qualification matrix is updated (flexibility chart)",            "Workforce Actions",     True),
    ("WF-3", "Implement buddy system for new hires — pair with experienced operators",          "Workforce Actions",     False),
    ("WF-4", "Communicate daily absenteeism status in shift meetings",                         "Workforce Actions",     False),
    ("WF-5", "Accelerate HR hiring pipeline if turnover is systemic",                          "Workforce Actions",     False),

    # ── Quality Readiness ─────────────────────────────────────────────────
    ("QR-1", "Update FTQ and BIQ targets to reflect transition period risk",                   "Quality Readiness",     True),
    ("QR-2", "Increase LPA frequency in all areas affected by workforce gap",                  "Quality Readiness",     True),
    ("QR-3", "Assess containment needs — activate 3rd-party containment if gap ≥ 15%",        "Quality Readiness",     True),
    ("QR-4", "Identify critical sorting / rework / EOL positions — ensure continuity",         "Quality Readiness",     True),
    ("QR-5", "Review safe launch matrix — extend monitoring period if FPY drops below target", "Quality Readiness",    False),

    # ── Quality Confirmation ──────────────────────────────────────────────
    ("QC-1", "Hold daily quality stand-up: Production / Quality / HR",                        "Quality Confirmation",  False),
    ("QC-2", "Track 1st-day and 1st-week incidents — root-cause analysis weekly",             "Quality Confirmation",  True),
    ("QC-3", "Monitor operator motivation and engagement — open escalation channel",           "Quality Confirmation",  False),
    ("QC-4", "Confirm FTQ and KPI monitoring dashboard active and reviewed daily",            "Quality Confirmation",  True),
    ("QC-5", "Document lessons learned — close all actions before returning to standard mode", "Quality Confirmation", False),
]


# ═════════════════════════════════════════════════════════════════════════════
# 6. CAPACITY CHANGE — per EAGP_5-3_ME_02
# ═════════════════════════════════════════════════════════════════════════════

_CAPACITY: List[Tuple] = [
    # Source: EAGP_5-3_ME_02_EN — Capacity Change Management procedure
    # All steps extracted from the PPT flow chart and notes

    # ── Quality Structure ─────────────────────────────────────────────────
    ("QS-1", "Confirm quality lead assigned to capacity change — include in multidisciplinary team",       "Quality Structure", False),
    ("QS-2", "Define quality gates for capacity ramp-up curve (RUC) approval and daily tracking",         "Quality Structure", False),
    ("QS-3", "Establish daily quality review during ramp-up period — assign responsible",                 "Quality Structure", False),

    # ── Customer Requirements ──────────────────────────────────────────────
    ("CR-1", "Receive and share capacity change request — establish schedule with multidisciplinary team", "Customer Requirements", False),
    ("CR-2", "Confirm ATV (Authorized Tooling Volumes) per customer authorisation — Step 1a",             "Customer Requirements", True),
    ("CR-3", "Negotiate with customer and communicate within organisation — confirm decision and timing",   "Customer Requirements", True),
    ("CR-4", "Get customer agreement on proposed capacity ramp-up schedule before execution",              "Customer Requirements", True),

    # ── Quality Readiness ─────────────────────────────────────────────────
    ("QR-1", "Define company finance impact — complete expense, price, investment repayment analysis",     "Quality Readiness", False),
    ("QR-2", "Sales reports customer-related investment supplement information to Finance",                "Quality Readiness", False),
    ("QR-3", "Prepare capacity adjustment (Man, Machine, Material, Method and Environment) — Step 4",      "Quality Readiness", True),
    ("QR-4", "Evaluate equipment, dies and tooling capacity — confirm sufficient for new volume",          "Quality Readiness", True),
    ("QR-5", "Provide raw material stock information and material transport plan",                         "Quality Readiness", False),
    ("QR-6", "Plan additional personnel demand and complete operator training before capacity start",       "Quality Readiness", False),
    ("QR-7", "If manufacturing system or flow changes: conduct PFMEA workshop — update control plan",      "Quality Readiness", True),
    ("QR-8", "Implement Statistical Process Control (SPC) and validate process capability at new volume",  "Quality Readiness", True),
    ("QR-9", "Define and document Ramp-Up Curve (RUC) — track daily quantity and quality output",         "Quality Readiness", True),

    # ── Quality Confirmation ──────────────────────────────────────────────
    ("QC-1", "Plant Quality / Reliability / AQP releases production area before start of new capacity",   "Quality Confirmation", True),
    ("QC-2", "Implement capacity adjustment — confirm adjusted manufacturing system and production area",  "Quality Confirmation", True),
    ("QC-3", "Track daily output vs. RUC plan — root-cause action if quantity or quality deviates",       "Quality Confirmation", True),
    ("QC-4", "Monitor process capability (Cpk) weekly during ramp-up confirmation period",                "Quality Confirmation", True),
    ("QC-5", "Increase LPA frequency during capacity ramp-up period",                                    "Quality Confirmation", False),
    ("QC-6", "Confirm full PPAP approval — no open quality issues before returning to standard mode",     "Quality Confirmation", True),
]



# ═════════════════════════════════════════════════════════════════════════════
# CUSTOMER-SPECIFIC QUALITY ITEMS
# Source: Versigent MO2 Quality Performance Review — VW slide
# Added automatically when customer matches
# ═════════════════════════════════════════════════════════════════════════════

_CUSTOMER_ITEMS = {
    "vw": [
        # Quality Structure
        ("VW-QS1", "Define VW IS quality team members and roles",                              "Quality Structure",     False),
        ("VW-QS2", "Define quality IH and DH structure per VW requirements",                  "Quality Structure",     False),
        # Customer Requirements
        ("VW-CR1", "Confirm VW portal access active for plant team",                          "Customer Requirements", False),
        ("VW-CR2", "Complete VW portal training for quality team",                            "Customer Requirements", False),
        ("VW-CR3", "Complete VDA training certification for quality team",                    "Customer Requirements", False),
        ("VW-CR4", "Complete VW Product audit training",                                      "Customer Requirements", False),
        ("VW-CR5", "Complete VW drawing specification training",                              "Customer Requirements", False),
        # Quality Readiness
        ("VW-QR1", "Gather lessons learned from VW & other similar projects — update KIM",    "Quality Readiness",     True),
        ("VW-QR2", "Complete PFMEA & control plan full alignment including Special Characteristics Validation", "Quality Readiness", True),
        ("VW-QR3", "Complete MSA & Capability study (Cp/Cpk) for all critical characteristics","Quality Readiness",   True),
        ("VW-QR4", "Complete VW line process release",                                        "Quality Readiness",     True),
        ("VW-QR5", "Complete VW line process readiness audit",                                "Quality Readiness",     True),
        ("VW-QR6", "Complete VW PPAP process approval",                                       "Quality Readiness",     True),
        ("VW-QR7", "Complete VW line process gap monitoring",                                 "Quality Readiness",     False),
        # Quality Confirmation
        ("VW-QC1", "Train quality inspectors on VW drawing and specification",                "Quality Confirmation",  False),
        ("VW-QC2", "Implement 100% control into process for WI with high impact on SC",      "Quality Confirmation",  True),
        ("VW-QC3", "Activate 100% EOL quality containment and firewall",                     "Quality Confirmation",  True),
        ("VW-QC4", "Validate final product 100% per drawing during RAMP UP CURVE",           "Quality Confirmation",  True),
        ("VW-QC5", "Increase teardown frequency to 1 piece per month",                       "Quality Confirmation",  False),
        ("VW-QC6", "Derive hourly, daily and weekly VOP / QIP Gemba reviews",                "Quality Confirmation",  False),
        ("VW-QC7", "Assign dedicated quality expert monitoring auditors during RC",           "Quality Confirmation",  False),
        ("VW-QC8", "Activate FTQ Approach Enhancement & KPIs Monitoring",                    "Quality Confirmation",  False),
    ],
    "renault": [
        ("RN-CR1", "Confirm ANPQP (Alliance NPQP) convergence gates aligned",                "Customer Requirements", True),
        ("RN-CR2", "Complete ASES audit preparation (Alliance Supplier Evaluation Standard)","Customer Requirements",  True),
        ("RN-QR1", "Complete Run @ Rate at OK Production milestone",                         "Quality Readiness",     True),
        ("RN-QR2", "Define CSL (Controlled Shipping Level) procedures",                     "Quality Readiness",     False),
        ("RN-QC1", "Activate 3PT (3 Panel Tool) for problem solving during launch",          "Quality Confirmation",  False),
    ],
    "stellantis": [
        ("ST-CR1", "Complete PSO (Process Sign-Off) preparation before SOP",                "Customer Requirements", True),
        ("ST-CR2", "Align GPS (Global Procurement Supplier) requirements",                  "Customer Requirements", True),
        ("ST-QR1", "Define CSL1 / CSL2 containment level readiness",                       "Quality Readiness",     True),
        ("ST-QR2", "Prepare PPAP per PSA-FCA combined manual",                             "Quality Readiness",     True),
        ("ST-QC1", "Monitor IPTV (Incidents Per Thousand Vehicles) target alignment",       "Quality Confirmation",  True),
    ],
    "mercedes": [
        ("MB-CR1", "Confirm MBST (Mercedes-Benz Special Terms) compliance",                 "Customer Requirements", True),
        ("MB-CR2", "Prepare MBN 10448 production process release documentation",           "Customer Requirements", True),
        ("MB-QR1", "Complete Daimler Supplier Portal (DSP) submission",                    "Quality Readiness",     True),
        ("MB-QR2", "Conduct 2-Day Production Run validation",                              "Quality Readiness",     True),
        ("MB-QR3", "Confirm VDA 6.3 audit score ≥ A grade",                               "Quality Readiness",     True),
        ("MB-QC1", "Declare Q-Stufe (Quality Level) per part per Mercedes standard",       "Quality Confirmation",  False),
    ],
    # ── Volvo ────────────────────────────────────────────────────────────────
    # Source: Volvo part/material standards supplied in /requirements
    # (electric cables, terminals, sleeves, LV connectors) + Volvo Cars
    # supplier quality requirements (IATF 16949 / APQP-PPAP / RSMS / IMDS).
    "volvo": [
        # Quality Structure
        ("VO-QS1", "Define Volvo program quality / APQP & SQE team and roles",                          "Quality Structure",     False),
        ("VO-QS2", "Confirm Volvo supplier portal access and program milestone reporting",              "Quality Structure",     False),
        # Customer Requirements
        ("VO-CR1", "Confirm IATF 16949 certification valid and registered with Volvo",                  "Customer Requirements", True),
        ("VO-CR2", "Obtain and review applicable Volvo part standards (STD/VCS) — cables, terminals, "
                   "sleeves and standardized LV connectors",                                            "Customer Requirements", True),
        ("VO-CR3", "Confirm RSMS — Restricted Substance Management Standard VCS 5036,5 — compliance "
                   "for all parts",                                                                      "Customer Requirements", True),
        ("VO-CR4", "Submit IMDS material data for all components — obtain Volvo approval",               "Customer Requirements", True),
        ("VO-CR5", "Complete Volvo drawing & GRS 10.03 specification training for the quality team",     "Customer Requirements", False),
        # Quality Readiness
        ("VO-QR1", "Complete PFMEA & Control Plan aligned with Volvo special characteristics",           "Quality Readiness",     True),
        ("VO-QR2", "Complete MSA & process capability (Cpk) study for all special characteristics",      "Quality Readiness",     True),
        ("VO-QR3", "Submit full PPAP package and obtain PSW approval before SOP",                        "Quality Readiness",     True),
        ("VO-QR4", "Complete Run @ Rate (R@R) capacity verification at agreed volume",                   "Quality Readiness",     True),
        ("VO-QR5", "Verify conductor rated area, colour code and part marking per Volvo cable standards","Quality Readiness",     False),
        ("VO-QR6", "Gather lessons learned / read-across from previous Volvo programs — update KIM",     "Quality Readiness",     False),
        # Quality Confirmation
        ("VO-QC1", "Train inspectors on Volvo drawings, colour code and GRS 10.03 specification",        "Quality Confirmation",  False),
        ("VO-QC2", "Activate 100% EOL containment and firewall for special characteristics at ramp-up",  "Quality Confirmation",  True),
        ("VO-QC3", "Validate finished harness 100% against Volvo-approved drawing during ramp-up curve", "Quality Confirmation",  True),
        ("VO-QC4", "Establish 8D problem-solving and Volvo defect reporting / escalation cadence",       "Quality Confirmation",  False),
    ],
}


# ═════════════════════════════════════════════════════════════════════════════
# MAP: program type → base checklist
# ═════════════════════════════════════════════════════════════════════════════

# ═════════════════════════════════════════════════════════════════════════════
# NEW PLANT LAUNCH
# Source: Aptiv New Plant Flawless Launch Support Initiative (Apr 2025)
#         RASIC table (timelines from screenshot)
#         4 gap categories: People / Process / Infrastructure / Customer
# All timeline references relative to SOP as stated in the RASIC table
# ═════════════════════════════════════════════════════════════════════════════

_NEW_PLANT: List[Tuple] = [

    # ── Quality Structure (People gap category) ───────────────────────────
    ("QS-1",  "Identify Mother / Sending Plant — formally engage quality team for support",
              "Quality Structure", True),
    ("QS-2",  "Define quality team structure for new plant — confirm IH/DH and RASIC roles "
              "(Cluster Quality, Site Quality, Reliability, CS Manager, APQP, PE, ME/Process)",
              "Quality Structure", True),
    ("QS-3",  "Assign new hires to mother / sending plant to learn routines before SOP",
              "Quality Structure", True),
    ("QS-4",  "Confirm expert support team from sister plants present from Process Release to "
              "4 Weeks after SOP",
              "Quality Structure", True),
    ("QS-5",  "Assess team seniority and capabilities — define training plan per gap identified",
              "Quality Structure", False),
    ("QS-6",  "Establish quality culture from day one — define QRQC boards "
              "(2 Weeks before SOP)",
              "Quality Structure", False),
    ("QS-7",  "Confirm needs and hiring plan on time — no position left unfilled at SOP",
              "Quality Structure", False),

    # ── Infrastructure Readiness ──────────────────────────────────────────
    ("IR-1",  "Perform Green Field Assessment — confirm automotive process knowhow baseline "
              "for new site",
              "Infrastructure Readiness", True),
    ("IR-2",  "Validate IT tools readiness: SAP, Holistech, DCiX, CAO, APRISO, ALS, PFT, "
              "QAuditor — all operational before SOP",
              "Infrastructure Readiness", True),
    ("IR-3",  "Confirm SOP Strategy — define production ramp-up plan and volume targets",
              "Infrastructure Readiness", True),
    ("IR-4",  "Validate metrology room: calibration conditions ensured, no manual records at SOP",
              "Infrastructure Readiness", True),
    ("IR-5",  "Ensure all measurement equipment received with approved certificates",
              "Infrastructure Readiness", True),
    ("IR-6",  "Verify measurement equipment received complete — no missing parts",
              "Infrastructure Readiness", True),
    ("IR-7",  "Confirm latest technology equipment received with datasheet and "
              "specification explanation",
              "Infrastructure Readiness", False),
    ("IR-8",  "Validate incoming inspection area ready — no early access impacting quality area "
              "readiness",
              "Infrastructure Readiness", False),
    ("IR-9",  "Confirm quantity of equipment is sufficient — not reduced due to cost constraint",
              "Infrastructure Readiness", False),
    ("IR-10", "Define standard file for Lessons Learned capitalisation — "
              "no ad-hoc approach at new site",
              "Infrastructure Readiness", False),

    # ── Quality Readiness (Process gap + RASIC items) ─────────────────────
    ("QR-1",  "Perform Critical Processes Assessment — 6 Weeks before SOP "
              "(Site Quality: S / Cluster Quality: S / Reliability: S / ME/Process: R)",
              "Quality Readiness", True),
    ("QR-2",  "Perform Plant Risk Assessment — 12 Weeks before SOP (CS Manager: R)",
              "Quality Readiness", True),
    ("QR-3",  "Receive historic quality issues from Mother Plant "
              "(Complaints / FTQ data) — 8 Weeks before SOP (Site Quality: R / Reliability: R)",
              "Quality Readiness", True),
    ("QR-4",  "Define PPAP Plan including customer PPAP and Run@Rate requirements — "
              "4 Weeks before SOP (Site Quality: R / CS Manager: S)",
              "Quality Readiness", True),
    ("QR-5",  "Complete Process Release — 4 Weeks before SOP "
              "(Site Quality: R / Reliability: S / ME/Process: S)",
              "Quality Readiness", True),
    ("QR-6",  "Identify Special and Key Product Characteristics — Pass-Through features "
              "identification & control — 4 Weeks before SOP "
              "(Site Quality: R / Reliability: S / CS Manager: S / ME/Process: S)",
              "Quality Readiness", True),
    ("QR-7",  "Review and validate Quality Master Plan — confirm standard QMP template used",
              "Quality Readiness", True),
    ("QR-8",  "Complete PFMEA and update Control Plan for new plant specificities",
              "Quality Readiness", True),
    ("QR-9",  "Validate quality areas readiness: Incoming Inspection, Metrology, Product Audit",
              "Quality Readiness", True),
    ("QR-10", "Complete equipment and tooling investment plan — confirm list of needed equipment",
              "Quality Readiness", False),
    ("QR-11", "Review Lessons Learned from previous plant start-ups — sister plant sharing",
              "Quality Readiness", False),

    # ── Quality Confirmation (Customer + Safe Launch section from RASIC) ──
    ("QC-1",  "Define Customer Protection Plan — 4 Weeks before SOP "
              "(Site Quality: A / Reliability: A / APQP: S / CS Manager: R)",
              "Quality Confirmation", True),
    ("QC-2",  "Activate Internal Safe Launch: containment, GP12, Sampling 100% — "
              "from SOP to 6 Weeks after SOP and/or following customer requirement "
              "(Site Quality: R / CS Manager: S)",
              "Quality Confirmation", True),
    ("QC-3",  "Perform PRA (Production Readiness Assessment) — "
              "1 Week after SOP & before customer visit "
              "(Site Quality: A / Reliability: A / APQP: R / CS Manager: A)",
              "Quality Confirmation", True),
    ("QC-4",  "Obtain PPAP Approval — 1 Week after SOP (CS Manager: A)",
              "Quality Confirmation", True),
    ("QC-5",  "Activate External support: CSE and support team for customer build — "
              "from 1st deliveries to end of GP12 (CS Manager: R)",
              "Quality Confirmation", True),
    ("QC-6",  "Confirm customer requirements application: PA Area, Metrology lab, TISAX, "
              "new technology preferred language",
              "Quality Confirmation", True),
    ("QC-7",  "Prepare and support Customer Site Assessment — align timing vs Plant Readiness",
              "Quality Confirmation", True),
    ("QC-8",  "Ensure OEM (Assembly plant) communication established before SOP",
              "Quality Confirmation", False),
    ("QC-9",  "Ensure Wiring Harness industry culture training completed for new hires",
              "Quality Confirmation", False),
    ("QC-10", "Monitor flawless launch metric — target 100% (Aptiv EMEA standard)",
              "Quality Confirmation", False),
]


_CHECKLISTS = {
    "new":       _NEW_PROGRAM,
    "new_plant": _NEW_PLANT,
    "transfer":  _BUSINESS_TRANSFER,
    "my_change": _MY_CHANGE,
    "restart":   _RESTART,
    "absence":   _ABSENCE,
    "capacity":  _CAPACITY,
}


# ═════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═════════════════════════════════════════════════════════════════════════════

def check_procedure_files() -> dict:
    """
    Reports file status in the sidebar.
    Since we no longer extract from files, all programs use the built-in
    quality checklists. Files are still listed for reference.
    """
    FILE_REFS = {
        "new":       "EANP_4-1_CS_01-03_EN.pptx",
        "new_plant": "New_Plant_Flawless_Launch_Initiative.pdf",
        "transfer":  "EAGP_4-4_MG_01-F01_EN.xlsx",
        "my_change": "EAEP_4-1_ME-EDS_10-01_EN.pptx",
        "restart":   "HOGP_5-1_MG-EDS_01-F01_EN.xlsx",
        "capacity":  "EAGP_5-3_ME_02_EN.pptx",
        "absence":   "built-in",
    }
    result = {}
    for prog, fname in FILE_REFS.items():
        fp = DATA / fname
        result[prog] = (fp.exists(), fname)
    return result


def load_checklist(
    program_type: str,
    context: dict = None,
    return_source: bool = False,
):
    """
    Returns the quality checklist for a given program type.

    Checklist is built from curated quality items (not extracted from files).
    Customer-specific items are appended automatically based on context.
    Context-aware items adapt based on inputs (e.g. KSK vs Batch).

    Parameters:
        program_type  : "new" | "transfer" | "my_change" | "restart" | "absence" | "capacity"
        context       : dict of user inputs for context-aware adaptation
        return_source : if True, returns (items, "quality-generated") tuple

    Returns:
        List[ChecklistItem]  or  (List[ChecklistItem], str)
    """
    context = context or {}
    source  = "quality-generated"

    raw = _CHECKLISTS.get(program_type, [])

    # Build base items
    items: List[ChecklistItem] = []
    for entry in raw:
        step, text, phase, critical = entry
        # Context adaptations
        text = _adapt_text(text, context)
        if text is None:
            continue   # item filtered out for this context
        items.append(ChecklistItem(
            step=step, text=text, phase=phase,
            critical=critical, warn=critical,
        ))

    # Context-specific state pre-marking
    items = _apply_state(items, program_type, context)

    # Append customer-specific quality items (deduplicated)
    # "default" = no customer confirmed yet — skip customer-specific items,
    # the plant readiness checklist is already complete without them
    customer = context.get("customer", "other")
    if customer != "default" and customer in _CUSTOMER_ITEMS:
        for entry in _CUSTOMER_ITEMS[customer]:
            step, text, phase, critical = entry
            # Only add if this item isn't already covered by the base checklist
            # (check by phase — avoid double-counting VW items for New Program)
            if not _is_covered(text, items):
                items.append(ChecklistItem(
                    step=step, text=text, phase=phase,
                    critical=critical, warn=critical,
                ))

    return (items, source) if return_source else items


def _adapt_text(text: str, context: dict) -> str:
    """
    Adapt item text based on context. Returns None to filter out the item.
    """
    prod_sys = context.get("prod_system", "batch")

    # KSK-specific wording
    if "Batch:" in text and "KSK:" in text:
        if prod_sys == "ksk":
            # Remove Batch part, keep KSK
            text = "KSK: " + text.split("KSK:")[1].strip()
        else:
            # Remove KSK part, keep Batch
            text = "Batch: " + text.split("|")[0].replace("Batch:", "").strip()

    # BMG only applies to VW
    if "BMG" in text and context.get("customer") != "vw":
        return None

    # PB2O only applies if KSK impact
    if "PB2O" in text and context.get("ksk_impact", "no") != "yes":
        return None

    # Multi-plant liaison only if multi-plant
    if "Liaison Coordinator" in text and "multiple plants" not in text:
        if context.get("multi_plant", "no") != "yes":
            return None

    return text


def _apply_state(
    items: List[ChecklistItem],
    program_type: str,
    context: dict,
) -> List[ChecklistItem]:
    """
    Pre-mark items as done/warn based on what the user has already told us.
    """
    # Restart: if prep was completed before shutdown, mark Shutdown Prep items done
    if program_type == "restart":
        prep_done = context.get("prep_status") == "complete"
        for item in items:
            if item.phase == "Shutdown Prep" and prep_done:
                item.done = True

    # MY Change: if feasibility rejected, mark feasibility item as critical warn
    if program_type == "my_change":
        if context.get("feasibility_status") == "rejected":
            for item in items:
                if "feasibility" in item.text.lower():
                    item.warn = True
                    item.critical = True

    # Capacity: if no flow change, unmark PFMEA item as critical
    if program_type == "capacity":
        if context.get("sys_flow_change", "no") == "no":
            for item in items:
                if "PFMEA" in item.text and "flow" in item.text.lower():
                    item.warn = False
                    item.critical = False

    # New Program: mark training/experience items as critical when team is new
    if program_type == "new":
        if context.get("np_experience") == "new":
            for item in items:
                if "experience" in item.text.lower() or "training plan" in item.text.lower():
                    item.critical = True
                    item.warn     = True

    # Business Transfer: warn on claim items when source plant has open claims
    if program_type == "transfer":
        has_claims = context.get("source_claims", "none") != "none"
        for item in items:
            if "claim" in item.text.lower():
                item.critical = has_claims
                item.warn     = has_claims

    return items


def _is_covered(text: str, items: List[ChecklistItem]) -> bool:
    """
    Check if a customer-specific item is already covered by the base checklist.
    Uses first 50 chars as a key to avoid near-duplicates.
    """
    key = text[:50].lower().strip()
    for item in items:
        if item.text[:50].lower().strip() == key:
            return True
        # Check for keyword overlap (catch paraphrases of the same action)
        if len(key) > 20:
            words = set(key.split())
            item_words = set(item.text[:50].lower().split())
            if len(words & item_words) >= 4:
                return True
    return False


def get_phases(items: List[ChecklistItem]) -> List[str]:
    """
    Returns unique phase names in the order they first appear.
    Used for tab grouping in the UI.
    """
    seen   = set()
    phases = []
    for item in items:
        if item.phase and item.phase not in seen:
            phases.append(item.phase)
            seen.add(item.phase)
    return phases
