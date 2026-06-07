# core/theme.py
# ─────────────────────────────────────────────────────────────────────────────
# Versigent Safe Launch — Design System runtime
#
# Single source of truth: design/tokens.json (W3C design-tokens format).
# This module resolves the token references and exposes:
#   • inject_theme()      -> emits global <style> (:root CSS vars + base + components)
#   • token(path)         -> resolved value, e.g. token("semantic.color.accent")
#   • RISK_COLORS / RISK_TEXT / RISK_BG  -> Python dicts for charts & f-strings
#
# Brand rule: copper #CD7925 is for borders/fills/badges; copper-700 (#9A5A14)
# is used whenever copper appears as TEXT on a light surface (WCAG AA >= 4.5:1).
# ─────────────────────────────────────────────────────────────────────────────

import json
import re
from functools import lru_cache
from pathlib import Path

_TOKENS_PATH = Path(__file__).parent.parent / "design" / "tokens.json"
_REF = re.compile(r"^\{([a-zA-Z0-9_.\-]+)\}$")


@lru_cache(maxsize=1)
def _raw():
    with open(_TOKENS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _lookup(data, dotted):
    node = data
    for part in dotted.split("."):
        node = node[part]
    # leaf token -> {"$value": ...}; group -> dict
    return node


def token(path):
    """Resolve a token path to its final string value, following {refs}."""
    data = _raw()
    node = _lookup(data, path)
    if isinstance(node, dict) and "$value" in node:
        val = node["$value"]
    else:
        val = node
    seen = 0
    while isinstance(val, str):
        m = _REF.match(val.strip())
        if not m or seen > 10:
            break
        ref = _lookup(data, m.group(1))
        val = ref["$value"] if isinstance(ref, dict) and "$value" in ref else ref
        seen += 1
    return val


def color(name, dark=False):
    """Resolved semantic color by short name (e.g. 'risk-high', 'foreground',
    'accent', 'surface-alt', 'risk-low-bg'), honoring dark mode. For Python-side
    use (Plotly charts) where CSS var() isn't available. Falls back to the light
    token when the name has no dark override."""
    if dark:
        d = _raw().get("theme", {}).get("dark", {})
        if name in d:
            return d[name]["$value"]
    return token("semantic.color." + name)


# ── Python-side palettes (resolved once) ─────────────────────────────────────
RISK_COLORS = {  # solid fills / badges / chart series
    "HIGH":   token("semantic.color.risk-high"),
    "MEDIUM": token("semantic.color.risk-medium"),
    "LOW":    token("semantic.color.risk-low"),
}
RISK_TEXT = {  # AA-safe text on light surfaces
    "HIGH":   token("semantic.color.risk-high-text"),
    "MEDIUM": token("semantic.color.risk-medium-text"),
    "LOW":    token("semantic.color.risk-low-text"),
}
RISK_BG = {  # tinted backgrounds
    "HIGH":   token("semantic.color.risk-high-bg"),
    "MEDIUM": token("semantic.color.risk-medium-bg"),
    "LOW":    token("semantic.color.risk-low-bg"),
}

NAVY   = token("semantic.color.foreground")
COPPER = token("semantic.color.accent")
COPPER_TEXT = token("semantic.color.accent-text")


def _css_variables():
    """Flatten primitive+semantic tokens into CSS custom properties."""
    t = token
    return f"""
  :root {{
    /* brand */
    --vg-navy: {t('primitive.color.navy.900')};
    --vg-navy-800: {t('primitive.color.navy.800')};
    --vg-copper: {t('primitive.color.copper.500')};
    --vg-copper-text: {t('primitive.color.copper.700')};
    --vg-gold: {t('primitive.color.gold.400')};

    /* semantic */
    --vg-bg: {t('semantic.color.background')};
    --vg-surface: {t('semantic.color.surface')};
    --vg-surface-alt: {t('semantic.color.surface-alt')};
    --vg-fg: {t('semantic.color.foreground')};
    --vg-muted: {t('semantic.color.muted-foreground')};
    --vg-border: {t('semantic.color.border')};
    --vg-accent: {t('semantic.color.accent')};
    --vg-accent-text: {t('semantic.color.accent-text')};

    /* risk */
    --vg-risk-high: {t('semantic.color.risk-high')};
    --vg-risk-high-text: {t('semantic.color.risk-high-text')};
    --vg-risk-high-bg: {t('semantic.color.risk-high-bg')};
    --vg-risk-med: {t('semantic.color.risk-medium')};
    --vg-risk-med-text: {t('semantic.color.risk-medium-text')};
    --vg-risk-med-bg: {t('semantic.color.risk-medium-bg')};
    --vg-risk-low: {t('semantic.color.risk-low')};
    --vg-risk-low-text: {t('semantic.color.risk-low-text')};
    --vg-risk-low-bg: {t('semantic.color.risk-low-bg')};

    /* typography */
    --vg-font-display: {t('primitive.fontFamily.display')};
    --vg-font-body: {t('primitive.fontFamily.body')};

    /* radius / shadow */
    --vg-radius-sm: {t('primitive.radius.sm')};
    --vg-radius: {t('primitive.radius.base')};
    --vg-radius-lg: {t('primitive.radius.lg')};
    --vg-shadow-card: {t('primitive.shadow.card')};
  }}"""


def _component_css():
    """Refined component classes — visually equivalent to the originals but
    token-driven and WCAG-corrected (copper text -> --vg-accent-text,
    muted text -> --vg-muted instead of the previous 2.5:1 gray)."""
    return """
  @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700&family=Barlow+Condensed:wght@600;700&display=swap');
  html, body, [class*="css"] { font-family: var(--vg-font-body); }

  .main-header {
    background: linear-gradient(135deg, var(--vg-navy) 0%, var(--vg-navy-800) 100%);
    padding: 16px 24px; border-bottom: none; border-radius: 0 0 16px 16px;
    margin: 0 -1rem 1.4rem -1rem;
    display: flex; align-items: center; justify-content: space-between;
  }
  .main-header h1 {
    color: #fff; font-family: var(--vg-font-display); font-size: 28px;
    font-weight: 700; letter-spacing: 1px; margin: 0;
  }
  .header-tag {
    background: rgba(247,169,0,0.12); border: 1px solid rgba(247,169,0,0.35);
    color: var(--vg-gold); padding: 4px 12px; border-radius: var(--vg-radius-sm);
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
  }
  .risk-badge {
    display: inline-block; padding: 6px 16px; border-radius: var(--vg-radius);
    font-family: var(--vg-font-display); font-size: 18px; font-weight: 700;
    letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;
  }
  .metric-card {
    background: var(--vg-surface);
    border: 1px solid var(--vg-border);
    border-radius: 16px; padding: 16px 18px; margin-bottom: 12px;
    box-shadow: var(--vg-shadow-card);
  }
  .metric-label {
    font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--vg-muted); margin-bottom: 4px; font-weight: 600;
  }
  .metric-value {
    font-family: var(--vg-font-display); font-size: 28px; font-weight: 700;
    color: var(--vg-fg); line-height: 1.1;
  }
  .metric-sub { font-size: 11px; color: var(--vg-muted); margin-top: 4px; }

  .chk-done { background: var(--vg-risk-low-bg); border-left: 3px solid var(--vg-risk-low);
              padding: 6px 10px; border-radius: var(--vg-radius-sm); font-size: 12px;
              color: var(--vg-risk-low-text); margin: 3px 0; }
  .chk-warn { background: var(--vg-risk-high-bg); border-left: 3px solid var(--vg-risk-high);
              padding: 6px 10px; border-radius: var(--vg-radius-sm); font-size: 12px;
              color: var(--vg-risk-high-text); margin: 3px 0; }
  .chk-todo { background: var(--vg-surface-alt); border-left: 3px solid var(--vg-border);
              padding: 6px 10px; border-radius: var(--vg-radius-sm); font-size: 12px;
              color: var(--vg-fg); margin: 3px 0; }

  .section-label {
    font-size: 11px; letter-spacing: 1.5px; text-transform: uppercase;
    color: var(--vg-muted); font-weight: 700;
    padding-bottom: 4px; margin: 14px 0 8px 0;
  }
  .file-ok   { background: var(--vg-surface-alt); border: 1px solid var(--vg-border);
               border-radius: 10px; padding: 6px 12px; font-size: 11px;
               color: var(--vg-fg); margin: 3px 0; }
  .file-miss { background: var(--vg-surface-alt); border: 1px solid var(--vg-border);
               border-radius: 10px; padding: 6px 12px; font-size: 11px;
               color: var(--vg-muted); margin: 3px 0; }

  /* Review phase header — clean iOS-style section header (no orange badge) */
  .review-phase-hdr {
    display:flex; align-items:center; justify-content:space-between;
    background: var(--vg-surface-alt); color: var(--vg-fg);
    padding: 9px 14px; border-radius: 12px; margin: 16px 0 6px;
    font-size: 12px; font-weight: 700; letter-spacing: .5px;
  }
  .review-count { color: var(--vg-muted); font-size: 11px; font-weight: 600; }

  /* Hide Streamlit's default top rainbow decoration + chrome */
  [data-testid="stDecoration"] { display: none !important; }
  #MainMenu {visibility:hidden;} footer {visibility:hidden;}
  [data-testid="stToolbar"] { display: none !important; }

  /* iOS-like rounding for native controls */
  .stButton > button, .stDownloadButton > button { border-radius: 12px; }
  [data-baseweb="input"], [data-baseweb="select"] > div,
  [data-baseweb="textarea"], .stTextInput input, .stNumberInput input,
  .stDateInput input { border-radius: 12px !important; }
  [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
  }"""


def _interactions_css():
    """Hover / focus / active / disabled states for interactive elements only.
    Follows the design-system rules: visible focus ring (never removed),
    subtle hover feedback + pointer cursor, dimmed disabled state, and
    transitions that respect prefers-reduced-motion. Applied to genuinely
    clickable controls — not to static info rows/cards."""
    return """
  /* Motion only when the user hasn't asked to reduce it */
  @media (prefers-reduced-motion: no-preference) {
    .stButton > button, .stDownloadButton > button, [data-baseweb="tab"],
    [data-testid="stExpander"] summary, a {
      transition: background-color .15s ease, border-color .15s ease,
                  box-shadow .15s ease, color .15s ease, transform .1s ease;
    }
  }

  /* Visible keyboard focus ring (brand copper) — applied on top of any
     widget's own styling so it is never effectively removed. */
  button:focus-visible, [role="button"]:focus-visible, a:focus-visible,
  input:focus-visible, textarea:focus-visible, select:focus-visible,
  [data-baseweb="tab"]:focus-visible, [data-testid="stExpander"] summary:focus-visible,
  [tabindex]:focus-visible {
    outline: 2px solid var(--vg-copper);
    outline-offset: 2px;
    border-radius: var(--vg-radius-sm);
  }
  /* baseweb inputs/selects manage focus on an inner div */
  [data-baseweb="select"]:focus-within,
  [data-baseweb="input"]:focus-within,
  [data-baseweb="textarea"]:focus-within {
    outline: 2px solid var(--vg-copper);
    outline-offset: 1px;
    border-radius: var(--vg-radius);
  }

  /* Buttons — hover/active/disabled */
  .stButton > button, .stDownloadButton > button { cursor: pointer; }
  .stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--vg-copper);
    color: var(--vg-copper-text);
    box-shadow: var(--vg-shadow-card);
  }
  .stButton > button:active, .stDownloadButton > button:active {
    transform: translateY(1px);
  }
  .stButton > button:disabled, .stDownloadButton > button:disabled {
    opacity: .5; cursor: not-allowed; box-shadow: none; transform: none;
  }
  /* Primary actions (Generate / export) — fill copper on hover */
  .stButton > button[kind="primary"]:hover,
  .stDownloadButton > button[kind="primary"]:hover {
    background: var(--vg-copper); border-color: var(--vg-copper); color: #fff;
  }

  /* Tabs */
  [data-baseweb="tab"]:hover { color: var(--vg-copper-text); cursor: pointer; }

  /* Expander header */
  [data-testid="stExpander"] summary { cursor: pointer; }
  [data-testid="stExpander"] summary:hover { color: var(--vg-copper-text); }

  /* Checkboxes / radios in the plan-review table */
  .stCheckbox label:hover, .stRadio label:hover { cursor: pointer; color: var(--vg-fg); }

  /* Links */
  a:hover { color: var(--vg-copper-text); }"""


def _responsive_css():
    """Mobile responsiveness. Streamlit ships fixed multi-column layouts that
    squish on phones; below 640px we stack columns, shrink the header and
    display type, and enforce >=44px touch targets (per the UX guidelines)."""
    return """
  /* No horizontal overflow on any device */
  html { -webkit-text-size-adjust: 100%; }
  [data-testid="stAppViewContainer"], section.main { overflow-x: hidden; }

  @media (max-width: 640px) {
    /* Tighter page gutters — use the full narrow viewport */
    .block-container, [data-testid="stMainBlockContainer"] {
      padding-left: 0.75rem !important; padding-right: 0.75rem !important;
      padding-top: 1rem !important;
    }

    /* Stack every column layout (KPIs, score+reco, review rows, downloads) */
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.5rem !important; }
    [data-testid="column"], [data-testid="stColumn"] {
      flex: 1 1 100% !important; min-width: 100% !important; width: 100% !important;
    }

    /* Header: compact, logo only, no overflow */
    .main-header { padding: 12px 16px; margin-left: -0.75rem; margin-right: -0.75rem; }
    .main-header h1 { font-size: 20px; }
    .vg-head-sub { display: none !important; }
    .main-header img { height: 26px !important; }

    /* Display type scales down */
    .metric-value { font-size: 22px; }
    .risk-badge { font-size: 15px; }
    .section-label { font-size: 9px; }

    /* Touch-friendly controls (>=44px) + full-width buttons */
    .stButton > button, .stDownloadButton > button {
      min-height: 44px; width: 100%;
    }
    [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; }

    /* Tables scroll instead of breaking the layout */
    [data-testid="stDataFrame"], .stTable { overflow-x: auto; }
  }"""


def _stepper_css():
    """Guided 4-step progress stepper at the top of the app."""
    return """
  .vg-stepper { display:flex; align-items:center; margin: 2px 0 24px; }
  .vg-step { display:flex; align-items:center; gap:10px; }
  .vg-step .num {
    width:36px; height:36px; border-radius:50%; flex:none;
    display:flex; align-items:center; justify-content:center;
    font-family: var(--vg-font-display); font-weight:700; font-size:17px;
    border:2px solid var(--vg-border); color: var(--vg-muted); background: var(--vg-bg);
  }
  .vg-step .lbl { font-size:12px; letter-spacing:1px; text-transform:uppercase;
                  color: var(--vg-muted); font-weight:700; white-space:nowrap; }
  .vg-step.active .num { border-color: var(--vg-accent); color:#fff; background: var(--vg-accent); }
  .vg-step.active .lbl { color: var(--vg-fg); }
  .vg-step.done .num  { border-color: var(--vg-accent); color: var(--vg-accent); background: transparent; }
  .vg-step.done .lbl  { color: var(--vg-fg); }
  .vg-connector { height:2px; background: var(--vg-border); flex:1 1 auto; margin:0 10px; min-width:16px; }
  .vg-connector.done { background: var(--vg-accent); }
  @media (max-width: 640px) {
    .vg-step .lbl { display:none; }
    .vg-step .num { width:30px; height:30px; font-size:14px; }
    .vg-connector { margin:0 6px; }
  }

  /* Hero / section helpers */
  .vg-section-title { font-family: var(--vg-font-display); font-size:20px; font-weight:700;
    color: var(--vg-fg); margin: 6px 0 2px; }
  .vg-section-sub { font-size:12px; color: var(--vg-muted); margin-bottom:10px; }
  .vg-gate { display:inline-flex; align-items:center; gap:6px; padding:6px 12px; margin:3px;
    border:1px solid var(--vg-border); border-radius:999px; font-size:12px; font-weight:600;
    color: var(--vg-fg); background: var(--vg-surface-alt); }
  .vg-gate .dot { width:8px; height:8px; border-radius:50%; background: var(--vg-accent); }"""


def _tabbar_css():
    """Fixed iOS-style bottom tab bar built from real Streamlit buttons.
    The bar = the horizontal block that contains our .vg-tabmark sentinel
    (selected via :has), so clicks rerun over the websocket and keep state."""
    return """
  .block-container { padding-bottom: 108px !important; }
  .vg-tabmark { display: none; }

  div[data-testid="stHorizontalBlock"]:has(.vg-tabmark) {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 1000;
    background: var(--vg-surface); border-top: 1px solid var(--vg-border);
    box-shadow: 0 -2px 14px rgba(22,40,63,0.07);
    padding: 6px 2px calc(6px + env(safe-area-inset-bottom));
    margin: 0 !important; gap: 0 !important;
    backdrop-filter: saturate(180%) blur(6px);
  }
  div[data-testid="stHorizontalBlock"]:has(.vg-tabmark) [data-testid="column"] {
    min-width: 0 !important; width: auto !important; flex: 1 1 0 !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.vg-tabmark) .stButton > button {
    width: 100%; background: transparent; border: none; box-shadow: none;
    color: var(--vg-muted); font-size: 11px; font-weight: 600; line-height: 1.35;
    white-space: pre-line; padding: 4px 2px; min-height: 0; border-radius: 10px;
    transition: color .15s ease, background .15s ease;
  }
  div[data-testid="stHorizontalBlock"]:has(.vg-tabmark) .stButton > button:hover {
    color: var(--vg-fg); background: var(--vg-surface-alt); border: none;
  }
  div[data-testid="stHorizontalBlock"]:has(.vg-tabmark) .stButton > button:disabled {
    opacity: .35; background: transparent;
  }"""


def _dark_css():
    """Dark mode: re-map the --vg-* semantic variables to the dark palette
    (tokens.json -> theme.dark) so every token-driven component flips
    automatically, then override the Streamlit chrome that ships light."""
    d = _raw()["theme"]["dark"]

    def v(key):
        return d[key]["$value"]

    return f"""
  /* ── Dark mode — re-assign semantic tokens ─────────────────────── */
  :root {{
    --vg-bg: {v('background')};
    --vg-surface: {v('surface')};
    --vg-surface-alt: {v('surface-alt')};
    --vg-fg: {v('foreground')};
    --vg-muted: {v('muted-foreground')};
    --vg-border: {v('border')};
    --vg-accent: {v('accent')};
    --vg-accent-text: {v('accent-text')};
    --vg-risk-high: {v('risk-high')};
    --vg-risk-high-text: {v('risk-high-text')};
    --vg-risk-high-bg: {v('risk-high-bg')};
    --vg-risk-med: {v('risk-medium')};
    --vg-risk-med-text: {v('risk-medium-text')};
    --vg-risk-med-bg: {v('risk-medium-bg')};
    --vg-risk-low: {v('risk-low')};
    --vg-risk-low-text: {v('risk-low-text')};
    --vg-risk-low-bg: {v('risk-low-bg')};
    --vg-shadow-card: 0 1px 3px rgba(0,0,0,0.45);
  }}

  /* ── Streamlit chrome (ships light — override to dark surfaces) ─── */
  .stApp,
  [data-testid="stAppViewContainer"],
  [data-testid="stHeader"] {{ background: var(--vg-bg); }}
  [data-testid="stSidebar"] {{ background: var(--vg-surface-alt); }}

  .stApp, [data-testid="stSidebar"],
  [data-testid="stMarkdownContainer"], p, span, li, label,
  h1, h2, h3, h4, h5, h6 {{ color: var(--vg-fg); }}

  /* Cards lift above the canvas */
  .metric-card {{ background: var(--vg-surface); }}
  .chk-todo {{ background: var(--vg-surface-alt); color: var(--vg-fg); }}

  /* Inputs / selects / textareas */
  [data-baseweb="input"], [data-baseweb="textarea"],
  [data-baseweb="select"] > div,
  .stTextInput input, .stNumberInput input, .stDateInput input, textarea {{
    background: var(--vg-surface) !important;
    color: var(--vg-fg) !important;
    border-color: var(--vg-border) !important;
  }}
  ::placeholder {{ color: var(--vg-muted) !important; }}

  /* Secondary buttons */
  .stButton > button, .stDownloadButton > button {{
    background: var(--vg-surface); color: var(--vg-fg);
    border-color: var(--vg-border);
  }}

  /* Dropdown / popover menus */
  [data-baseweb="popover"] [role="listbox"],
  [data-baseweb="menu"] {{ background: var(--vg-surface); color: var(--vg-fg); }}

  /* Dataframes & code */
  [data-testid="stDataFrame"] {{ background: var(--vg-surface); }}
  code {{ background: var(--vg-surface-alt); color: var(--vg-accent-text); }}

  /* Alerts (st.success / st.info / st.warning) — keep on a dark surface */
  [data-testid="stAlert"], [data-baseweb="notification"] {{
    background: var(--vg-surface) !important; color: var(--vg-fg) !important;
    border: 1px solid var(--vg-border);
  }}
  [data-testid="stAlert"] * {{ color: var(--vg-fg) !important; }}

  /* Expander body */
  [data-testid="stExpander"] details {{
    background: var(--vg-surface); border-color: var(--vg-border);
  }}"""


def inject_theme(st, dark=False):
    """Inject the full design-system stylesheet. Call once, right after
    st.set_page_config(). `st` is the streamlit module. Pass dark=True to
    flip to the Versigent dark palette."""
    css = (_css_variables() + _component_css() + _interactions_css()
           + _stepper_css() + _tabbar_css() + _responsive_css())
    if dark:
        css += _dark_css()  # appended last so the overrides win
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)
