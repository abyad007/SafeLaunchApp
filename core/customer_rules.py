# core/customer_rules.py
# ─────────────────────────────────────────────────────────────────────────────
# Stores every OEM's customer-specific requirements and score bonus.
# A "dict" (dictionary) in Python maps keys to values: {"key": value}
# You access a value with: CUSTOMER_RULES["vw"]  or  CUSTOMER_RULES.get("vw")
# ─────────────────────────────────────────────────────────────────────────────

# Each entry is a dict with:
#   name        : display name
#   score_bonus : extra risk points added to any program for this customer
#   items       : list of strings — the specific requirements
#   gates       : customer-specific quality gates

CUSTOMER_RULES: dict = {

    "vw": {
        "name": "Volkswagen",
        "score_bonus": 8,
        "color": "#1A3C6E",   # VW brand blue for display
        "items": [
            "VW Formel Q — supplier capability assessment required",
            "VW 99000 — process audit before SOP",
            "VDA 6.3 process audit (Score ≥ A grade)",
            "PPA process per VDA standard",
            "8D problem solving methodology mandatory",
            "KSK / Batch declaration required for harness products",
            "Run @ Rate validation at SOP - 2 weeks",
            "BMG (Build Sample Approval) — mandatory for new programs",
            "VW portal access + VDA training certification",
        ],
        "gates": ["RR", "PDR", "IDR", "CDR", "PRR", "SB", "CD", "CA", "FA", "PA", "CT"],
    },

    "renault": {
        "name": "Renault",
        "score_bonus": 6,
        "color": "#EFDF00",   # Renault yellow
        "items": [
            "ANPQP (Alliance NPQP) — Renault-Nissan-Mitsubishi standard",
            "ASES audit (Alliance Supplier Evaluation Standard)",
            "Convergence ANPQP gates at each milestone",
            "Run @ Rate at OK Production",
            "CSL (Controlled Shipping Level) procedures defined",
            "3PT (3 Panel Tool) for problem solving",
        ],
        "gates": ["SB", "CD", "CA", "FA", "PA", "CT"],
    },

    "stellantis": {
        "name": "Stellantis",
        "score_bonus": 7,
        "color": "#C00D1E",   # Stellantis red
        "items": [
            "PSO (Process Sign-Off) at SOP — mandatory",
            "GPS (Global Procurement Supplier) requirements",
            "CSL1 / CSL2 containment levels readiness",
            "PFMEA per AIAG-VDA standard",
            "PPAP per PSA-FCA combined manual",
            "IPTV (Incidents Per Thousand Vehicles) target alignment",
        ],
        "gates": ["SB", "CD", "CA", "FA", "PA", "CT"],
    },

    "mercedes": {
        "name": "Mercedes-Benz",
        "score_bonus": 9,
        "color": "#222222",   # Mercedes dark
        "items": [
            "MBST (Mercedes-Benz Special Terms) compliance",
            "MBN 10448 — production process release",
            "Daimler Supplier Portal (DSP) submission",
            "2-Day Production Run validation",
            "Q-Stufe (Quality level) declared per part",
            "VDA 6.3 audit ≥ A grade required",
            "Self-released supplier status review",
        ],
        "gates": ["SB", "CD", "CA", "FA", "PA", "CT"],
    },

    "volvo": {
        "name": "Volvo",
        "score_bonus": 8,
        "color": "#003057",   # Volvo deep blue
        "items": [
            # Customer requirements
            "IATF 16949 certification valid and registered with Volvo",
            "APQP & PPAP per AIAG — PSW submission and approval before SOP",
            "Run @ Rate (R@R) capacity verification before SOP",
            "8D problem-solving methodology mandatory for all quality issues",
            "Volvo supplier portal access + program milestone reporting",
            # Specific requirements — applicable Volvo part standards (data/../requirements)
            "Comply with applicable Volvo Corporate / Car Standards (STD/VCS): "
            "electric cables (S2, R2, RK90, RT, SK90, R2IB, R2A2, MKFK, R2KB, RKKB, "
            "R33, 2ZGE, 3ZCF), cable sleeves, ring terminals and standardized LV connectors",
            "Verify conductor rated area, colour code and part marking per the cable standards",
            # Quality norms
            "RSMS — Restricted Substance Management Standard VCS 5036,5 — compliance for all parts",
            "IMDS (International Material Data System) material data submitted and approved",
            "GRS 10.03 proprietary handling + drawing/specification control",
            "MSA & SPC capability (Cpk) demonstrated on all special characteristics",
        ],
        "gates": ["SB", "CD", "CA", "FA", "PA", "CT"],
    },

    "default": {
        "name": "No Customer Assigned Yet",
        "score_bonus": 0,
        "color": "#6B7280",
        "items": [
            "No customer confirmed — plant readiness preparation in progress",
            "Apply IATF 16949 baseline requirements for all quality areas",
            "Define Customer Protection Plan ready to activate once customer confirmed",
            "Prepare PPAP package framework — finalise on customer confirmation",
            "Ensure IT tools (SAP, DCiX, CAO) ready to configure for any OEM",
            "Complete Green Field / Plant Risk Assessment independent of customer",
            "Define quality team RASIC — roles to be confirmed per customer requirement",
        ],
        "gates": ["SB", "CD", "CA", "FA", "PA", "CT"],
    },
    "other": {
        "name": "Other Customer",
        "score_bonus": 0,
        "color": "#6B7280",
        "items": [
            "Apply standard APQP / IATF 16949 requirements",
            "No customer-specific rules pre-loaded",
        ],
        "gates": ["SB", "CD", "CA", "FA", "PA", "CT"],
    },
}


def get_customer(customer_key: str) -> dict:
    """
    Safe lookup — returns 'other' if the key doesn't exist.
    The .get(key, default) method returns default when key is missing.
    """
    return CUSTOMER_RULES.get(customer_key, CUSTOMER_RULES["other"])
