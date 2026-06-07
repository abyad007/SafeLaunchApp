# app.py
# ─────────────────────────────────────────────────────────────────────────────
# Versigent Safe Launch Generator — guided 4-step interactive dashboard.
# Flow: ① Configurer → ② Tableau de bord → ③ Revue → ④ Export
# Run with:  python -m streamlit run app.py
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import streamlit.components.v1 as components
import json
import math
from pathlib import Path
from datetime import date, timedelta, datetime

from core.scoring_engine   import calculate_score
from core.checklist_loader  import load_checklist, get_phases, ChecklistItem
from core.customer_rules    import get_customer
from core.report_generator  import generate_ppt, generate_excel, _build_kpis
from core.procedure_reader  import scan_new_files, extract_from_file, ExtractionResult, auto_classify_file, _PROG_LABELS
from core.llm_extractor     import get_llm_status
from core.theme             import inject_theme, RISK_COLORS, RISK_TEXT
from core import charts

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Versigent Safe Launch",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT  = Path(__file__).parent
PLANS = ROOT / "data" / "plans"

PROGRAM_OPTIONS = {
    "":           "— Select Program Type —",
    "new":        "New Program",
    "new_plant":  "New Plant Launch",
    "transfer":   "Business Transfer",
    "my_change":  "MY Change / Engineering Change",
    "restart":    "Restart After Shutdown",
    "absence":    "Absence / Turnover (High)",
    "capacity":   "Capacity Change",
}

CUSTOMER_OPTIONS = {
    "vw":         "Volkswagen",
    "renault":    "Renault",
    "stellantis": "Stellantis",
    "mercedes":   "Mercedes-Benz",
    "volvo":      "Volvo",
    "other":      "Other",
}

CUSTOMER_OPTIONS_NEW_PLANT = {
    "default":    "No customer assigned yet — plant readiness mode",
    "vw":         "Volkswagen",
    "renault":    "Renault",
    "stellantis": "Stellantis",
    "mercedes":   "Mercedes-Benz",
    "volvo":      "Volvo",
    "other":      "Other",
}

DARK = st.session_state.get("dark_mode", False)
inject_theme(st, dark=DARK)

# ── Header — SVG logo embedded inline ────────────────────────────────────
_LOGO_SVG = """<svg viewBox='0 0 1408.58 287.36' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' id='Layer_2' overflow='hidden'><defs/><g id='Layer_1-2'><g><g><path d='M314.68 40.91 347.97 40.91 400.63 194.26 453.84 40.91 486.31 40.91 419.46 231.91 381.81 231.91 314.69 40.91Z' fill='#FFFFFF'/><path d='M475.53 124.23C481.26 113.41 489.26 105.04 499.54 99.13 509.82 93.22 521.6 90.26 534.88 90.26 548.16 90.26 560.21 92.99 570.49 98.45 580.76 103.91 588.86 111.64 594.78 121.64 600.69 131.65 603.74 143.38 603.92 156.84 603.92 160.48 603.65 164.21 603.1 167.91L497.58 167.91 497.58 169.66C498.5 181.85 502.32 191.49 509.23 198.58 516.14 205.67 525.33 209.22 536.79 209.22 545.88 209.22 553.53 207.08 559.71 202.81 565.89 198.54 569.98 192.49 571.99 184.9L601.46 184.9C598.91 198.85 592.05 210.49 580.86 219.59 569.67 228.69 555.71 233.23 538.97 233.23 524.41 233.23 511.73 230.28 500.9 224.36 490.07 218.45 481.71 210.13 475.8 199.39 469.89 188.66 466.93 176.2 466.93 162.01 466.93 147.82 469.79 135.04 475.53 124.22ZM573.9 146.91C572.62 136.72 568.58 128.76 561.76 123.03 554.94 117.3 546.34 114.43 535.97 114.43 526.33 114.43 518 117.39 511 123.3 503.99 129.21 499.95 137.08 498.86 146.9L573.9 146.9Z' fill='#FFFFFF'/><path d='M692.58 91.91 692.58 119.91 679.41 119.91C667.16 119.91 658.29 123.86 652.8 131.76 647.31 139.66 644.57 149.7 644.57 161.87L644.57 231.9 615.57 231.9 615.57 91.91 641.69 91.91 644.95 112.96C648.94 106.4 654.11 101.25 660.46 97.51 666.81 93.78 675.33 91.9 686.04 91.9L692.57 91.9Z' fill='#FFFFFF'/><path d='M725.18 185.91C725.73 193.22 729.16 199.21 735.46 203.87 741.77 208.53 749.95 210.86 760 210.86 768.95 210.86 776.22 209.17 781.8 205.79 787.37 202.41 790.16 197.89 790.16 192.22 790.16 187.47 788.88 183.9 786.32 181.53 783.76 179.16 780.33 177.46 776.04 176.46 771.74 175.46 765.11 174.4 756.16 173.31 743.91 171.85 733.81 169.88 725.86 167.41 717.91 164.94 711.51 161.01 706.67 155.62 701.82 150.23 699.4 142.96 699.4 133.82 699.4 125.23 701.82 117.6 706.67 110.92 711.51 104.25 718.19 99.09 726.69 95.43 735.19 91.78 744.83 89.95 755.62 89.95 773.35 89.95 787.74 93.88 798.81 101.74 809.87 109.6 815.85 120.66 816.77 134.92L787.98 134.92C787.25 128.52 784.05 123.27 778.38 119.15 772.71 115.04 765.58 112.98 756.99 112.98 748.4 112.98 741.45 114.63 736.15 117.92 730.85 121.21 728.2 125.69 728.2 131.36 728.2 135.57 729.52 138.72 732.18 140.82 734.83 142.92 738.17 144.38 742.19 145.21 746.21 146.03 752.7 146.99 761.66 148.09 773.73 149.37 783.87 151.34 792.1 153.99 800.33 156.64 806.91 160.84 811.84 166.6 816.78 172.36 819.24 180.17 819.24 190.04 819.24 198.81 816.68 206.54 811.56 213.21 806.44 219.88 799.4 225 790.45 228.56 781.49 232.12 771.44 233.91 760.29 233.91 741.46 233.91 726.24 229.66 714.64 221.16 703.03 212.66 697.04 200.92 696.68 185.93L725.2 185.93Z' fill='#FFFFFF'/><path d='M860.96 41C864.41 44.37 866.14 48.6 866.14 53.69 866.14 58.78 864.41 63.01 860.96 66.38 857.5 69.75 853.23 71.43 848.13 71.43 843.03 71.43 838.76 69.75 835.3 66.38 831.84 63.02 830.12 58.79 830.12 53.69 830.12 48.59 831.85 44.37 835.3 41 838.75 37.64 843.03 35.95 848.13 35.95 853.23 35.95 857.5 37.63 860.96 41ZM833.58 91.91 862.58 91.91 862.58 231.91 833.58 231.91 833.58 91.91Z' fill='#FFFFFF'/><path d='M1018.58 91.91 1018.58 225.57C1018.58 245.17 1012.79 260.37 1001.23 271.17 989.67 281.97 971.78 287.37 947.57 287.37 928.78 287.37 913.51 283.15 901.77 274.71 890.02 266.27 883.52 254.34 882.26 238.91L912.07 238.91C913.87 246.71 918.03 252.75 924.54 257.01 931.05 261.27 939.45 263.41 949.75 263.41 976.31 263.41 989.59 250.43 989.59 224.48L989.59 208.96C979.47 224.2 964.38 231.83 944.33 231.83 931.68 231.83 920.39 228.97 910.45 223.25 900.51 217.53 892.74 209.37 887.14 198.75 881.54 188.13 878.74 175.57 878.74 161.05 878.74 146.53 881.59 134.74 887.28 124.03 892.97 113.32 900.78 105.02 910.72 99.12 920.65 93.22 931.86 90.27 944.33 90.27 954.81 90.27 963.84 92.36 971.43 96.53 979.02 100.71 985.16 106.42 989.86 113.68L993.11 91.9 1018.59 91.9ZM978.62 194.63C986.08 186.17 989.81 175.21 989.81 161.75 989.81 148.29 986.08 136.69 978.62 128.05 971.16 119.41 961.33 115.09 949.15 115.09 936.97 115.09 927.14 119.37 919.68 127.91 912.22 136.46 908.49 147.56 908.49 161.2 908.49 174.84 912.22 185.94 919.68 194.49 927.14 203.04 936.96 207.31 949.15 207.31 961.34 207.31 971.16 203.08 978.62 194.62Z' fill='#FFFFFF'/><path d='M1039.88 124.23C1045.61 113.41 1053.61 105.04 1063.89 99.13 1074.17 93.22 1085.95 90.26 1099.23 90.26 1112.51 90.26 1124.56 92.99 1134.84 98.45 1145.11 103.91 1153.21 111.64 1159.13 121.64 1165.04 131.65 1168.09 143.38 1168.27 156.84 1168.27 160.48 1168 164.21 1167.45 167.91L1062.58 167.91 1062.58 169.66C1062.84 181.85 1066.66 191.49 1073.58 198.58 1080.49 205.67 1089.68 209.22 1101.14 209.22 1110.23 209.22 1117.88 207.08 1124.06 202.81 1130.24 198.54 1134.33 192.49 1136.34 184.9L1165.81 184.9C1163.26 198.85 1156.4 210.49 1145.21 219.59 1134.02 228.69 1120.06 233.23 1103.32 233.23 1088.76 233.23 1076.08 230.28 1065.25 224.36 1054.42 218.45 1046.06 210.13 1040.15 199.39 1034.24 188.66 1031.28 176.2 1031.28 162.01 1031.28 147.82 1034.14 135.04 1039.88 124.22ZM1138.25 146.91C1136.97 136.72 1132.93 128.76 1126.11 123.03 1119.29 117.3 1110.69 114.43 1100.32 114.43 1090.68 114.43 1082.35 117.39 1075.35 123.3 1068.34 129.21 1064.3 137.08 1063.21 146.9L1138.25 146.9Z' fill='#FFFFFF'/><path d='M1293.87 105.58C1304.34 115.79 1309.57 132.2 1309.57 154.8L1309.57 231.91 1280.57 231.91 1280.57 156.6C1280.57 143.32 1277.73 133.23 1272.07 126.31 1266.4 119.4 1258.09 115.94 1247.12 115.94 1235.42 115.94 1226.24 119.99 1219.57 128.08 1212.9 136.18 1209.56 147.32 1209.56 161.51L1209.56 231.91 1179.56 231.91 1179.56 91.91 1205.23 91.91 1208.51 110.23C1219.07 96.93 1234 90.27 1253.3 90.27 1269.87 90.27 1283.38 95.38 1293.86 105.58Z' fill='#FFFFFF'/><path d='M1341.58 117.91 1317.58 117.91 1317.58 91.91 1341.58 91.91 1341.58 52.91 1370.58 52.91 1370.58 91.91 1404.58 91.91 1404.58 117.91 1371.58 117.91 1371.58 190.88C1371.58 196.35 1372.68 200.22 1374.87 202.49 1377.06 204.77 1380.81 205.91 1386.11 205.91L1408.58 205.91 1408.58 231.91 1380.02 231.91C1366.66 231.91 1356.91 228.81 1350.78 222.62 1344.65 216.43 1341.58 206.86 1341.58 193.91L1341.58 117.91Z' fill='#FFFFFF'/></g><g><path d='M82.69 101.48C100.11 119.3 113.74 140.7 126.93 161.4 139.12 180.53 150.68 198.66 164.53 213.03 162.08 205.49 160.31 197.45 159.21 188.76 156.44 167.01 158.18 144.04 159.87 121.8 163.15 78.61 166.01 34.83 135.58-0.01 86.97 0.15 44.37 25.8 20.44 64.27 43.85 70.41 64.24 82.59 82.69 101.47Z' fill='#CD7924'/><path d='M136.2 231.47C121.31 215.38 109.38 195.67 97.83 176.6 75.43 139.58 52.33 102.34 7.41 91.63 2.61 105.53 0 120.46 0 136 0 211.11 60.89 272 136 272 152.78 272 168.84 268.95 183.68 263.4 165.82 257.27 150.57 246.98 136.21 231.47Z' fill='#CD7924'/><path d='M176.46 6.03C183.88 19.69 188.84 34.87 191.48 51.88 195.3 76.51 193.96 101.84 192.66 126.35 191.38 150.69 190.16 173.67 193.97 194.61 197.48 213.9 205.02 229.25 216.95 241.37 217.16 241.4 217.36 241.44 217.57 241.46L217.57 241.98C218.15 242.56 218.74 243.13 219.34 243.69 251.54 218.82 272.28 179.83 272.28 136 272.28 74.87 231.95 23.17 176.45 6.03Z' fill='#CD7924'/></g></g></g></svg>"""

_HEADER_HTML = (
    '<div class="main-header">' +
    '<div style="display:flex;align-items:center;gap:18px;">' +
    '<div style="height:32px;display:flex;align-items:center;">' +
    '<img src="data:image/svg+xml;base64,' + __import__("base64").b64encode(
        _LOGO_SVG.encode()
    ).decode() + '" style="height:32px;width:auto;" alt="Versigent"/>' +
    '</div>' +
    '<span class="vg-head-sub" style="display:flex;align-items:center;gap:18px;">' +
    '<span style="width:1px;height:28px;background:rgba(255,255,255,0.18);"></span>' +
    '<span style="color:rgba(255,255,255,0.5);font-family:Barlow Condensed,sans-serif;' +
    'font-size:13px;letter-spacing:2px;text-transform:uppercase;font-weight:600;">' +
    'Safe Launch Generator</span></span>' +
    '</div>' +
    '</div>'
)
st.markdown(_HEADER_HTML, unsafe_allow_html=True)

# ── Wizard state ────────────────────────────────────────────────────────────
st.session_state.setdefault("step", 1)

_STEPS = [(1, "Configurer"), (2, "Tableau de bord"), (3, "Revue"), (4, "Export")]
_DATE_LABEL = {"new": "SOP", "transfer": "SOP", "my_change": "Implementation",
               "restart": "Restart", "capacity": "Capacity Change", "absence": "Effective",
               "new_plant": "SOP"}


def _goto(step):
    st.session_state["step"] = step
    st.rerun()


def _reset_plan():
    for k in ("result", "checklist", "checklist_source", "stored_prog_type",
              "part_name", "meta", "customer_name", "inputs"):
        st.session_state.pop(k, None)
    st.session_state["step"] = 1


# ═════════════════════════════════════════════════════════════════════════════
# TOP BAR (controls — no desktop sidebar, app-like)
# ═════════════════════════════════════════════════════════════════════════════
def render_topbar():
    if "llm_status" not in st.session_state:
        st.session_state["llm_status"] = get_llm_status()
    c_toggle, c_reset, _spacer = st.columns([2, 2, 6])
    with c_toggle:
        st.toggle("🌙 Sombre", key="dark_mode", help="Thème clair / sombre")
    with c_reset:
        if "result" in st.session_state:
            if st.button("＋ Nouveau", use_container_width=True,
                         help="Effacer le plan courant et recommencer"):
                _reset_plan()
                st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# STEPPER
# ═════════════════════════════════════════════════════════════════════════════
def render_stepper(step):
    html = ['<div class="vg-stepper">']
    for i, (num, lbl) in enumerate(_STEPS, start=1):
        cls = "active" if i == step else ("done" if i < step else "")
        mark = "✓" if i < step else str(num)
        html.append(f'<div class="vg-step {cls}"><div class="num">{mark}</div>'
                    f'<div class="lbl">{lbl}</div></div>')
        if i < len(_STEPS):
            html.append(f'<div class="vg-connector {"done" if i < step else ""}"></div>')
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def _section(title, sub=""):
    st.markdown(f'<div class="vg-section-title">{title}</div>'
                + (f'<div class="vg-section-sub">{sub}</div>' if sub else ""),
                unsafe_allow_html=True)


# iOS bottom tab bar — real Streamlit buttons (state-preserving), pinned via CSS.
# Emoji icon on line 1, label on line 2 (white-space:pre-line in _tabbar_css).
_TABS = [(1, "Config"), (2, "Tableau"), (3, "Revue"), (4, "Export")]


def render_tabbar(step, has_result):
    cols = st.columns(4)
    for i, (n, label) in enumerate(_TABS):
        with cols[i]:
            if i == 0:
                st.markdown('<span class="vg-tabmark"></span>', unsafe_allow_html=True)
            disabled = n > 1 and not has_result
            if st.button(label, key=f"tab_{n}", disabled=disabled,
                         use_container_width=True) and step != n:
                st.session_state["step"] = n
                st.rerun()
    # Highlight the active tab (nth column) — injected per current step
    st.markdown(
        '<style>div[data-testid="stHorizontalBlock"]:has(.vg-tabmark) '
        f'[data-testid="column"]:nth-child({step}) .stButton > button'
        '{color:var(--vg-fg)!important;font-weight:700!important;}</style>',
        unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PROCEDURE IMPORT (preview + add to plan) — used inside Step 1
# ═════════════════════════════════════════════════════════════════════════════
def render_procedure_preview():
    if not (st.session_state.get("preview_file")):
        return
    fp = Path(st.session_state["preview_file"])
    if st.session_state.get("preview_result") is None:
        with st.spinner(f"Reading {fp.name}…"):
            st.session_state["preview_result"] = extract_from_file(fp)
    result_pr: ExtractionResult = st.session_state["preview_result"]

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#16283F,#1F3553);
                border-left:5px solid #CD7925;border-radius:8px;padding:16px 22px;margin:8px 0 16px;">
      <div style="color:rgba(255,255,255,0.7);font-size:9px;letter-spacing:2px;text-transform:uppercase;font-weight:700;">Procedure Preview</div>
      <div style="color:white;font-size:18px;font-weight:700;font-family:'Barlow Condensed',sans-serif;margin-top:2px;">{fp.name}</div>
      <div style="color:rgba(255,255,255,0.55);font-size:12px;margin-top:4px;">
        {"Error: " + result_pr.error if result_pr.error
         else f"{result_pr.item_count} quality items · {len(result_pr.phases)} phase(s) · "
              f"Source: {getattr(result_pr, 'source_method', 'rule-based').upper()}"}
      </div>
    </div>
    """, unsafe_allow_html=True)

    if result_pr.error or result_pr.item_count == 0:
        if result_pr.error:
            st.error(f"Could not read this file: {result_pr.error}")
        else:
            st.warning("No quality action items detected in this file.")
        if st.button("Close preview"):
            st.session_state.pop("preview_file", None)
            st.session_state.pop("preview_result", None)
            st.rerun()
        return

    sel_key = f"sel_{fp.name}"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = {it.step: True for it in result_pr.items}
    sel_state = st.session_state[sel_key]

    phases_pr = result_pr.phases or ["All Items"]
    for tab, phase in zip(st.tabs(phases_pr), phases_pr):
        with tab:
            phase_items = [i for i in result_pr.items if i.phase == phase] \
                if phase != "All Items" else result_pr.items
            ph_checked = all(sel_state.get(i.step, True) for i in phase_items)
            if st.button("Deselect all" if ph_checked else "Select all",
                         key=f"tog_pr_{fp.name}_{phase}"):
                for i in phase_items:
                    sel_state[i.step] = not ph_checked
                st.rerun()
            for item in phase_items:
                col_chk, col_txt = st.columns([0.4, 6])
                with col_chk:
                    checked = st.checkbox("✓", value=sel_state.get(item.step, True),
                                          key=f"pr_{fp.name}_{item.step}",
                                          label_visibility="collapsed")
                    sel_state[item.step] = checked
                with col_txt:
                    bdr = "var(--vg-risk-high)" if item.critical else "var(--vg-border)"
                    bg = "var(--vg-risk-high-bg)" if item.critical else "var(--vg-surface-alt)"
                    alpha = "1" if checked else "0.38"
                    badge = " 🔴" if item.critical else ""
                    st.markdown(
                        f'<div style="border-left:3px solid {bdr};background:{bg};'
                        'border-radius:3px;padding:5px 10px;font-size:12px;'
                        f'color:var(--vg-fg);opacity:{alpha};">'
                        '<strong style="font-family:monospace;color:var(--vg-accent-text);font-size:10px;">'
                        f'{item.step}</strong>&nbsp;&nbsp;{item.text}{badge}</div>',
                        unsafe_allow_html=True)

    n_selected = sum(1 for v in sel_state.values() if v)
    auto_prog = st.session_state.get("preview_prog", "unknown")
    auto_prog_label = _PROG_LABELS.get(auto_prog, "Unclassified")
    can_add = auto_prog != "unknown"

    add_col1, add_col2 = st.columns([5, 1])
    with add_col1:
        if can_add:
            st.markdown(
                '<div style="padding:10px 14px;background:var(--vg-risk-low-bg);'
                'border:1px solid var(--vg-risk-low);border-radius:6px;font-size:13px;color:var(--vg-fg);">'
                f'<strong>{n_selected} items</strong> will be added to '
                f'<strong>{auto_prog_label}</strong>.</div>', unsafe_allow_html=True)
        else:
            st.warning("Could not identify the program type. Rename the file with a "
                       "recognisable keyword (transfer, restart, capacity…) and retry.")
    with add_col2:
        if can_add and st.button("Add to Plan", type="primary", use_container_width=True):
            extra_key = f"extra_items_{auto_prog}"
            existing = st.session_state.get(extra_key, [])
            new_items = [ChecklistItem(step=it.step, text=it.text,
                                       phase=it.phase or "Procedure Items",
                                       critical=it.critical, warn=it.critical)
                         for it in result_pr.items if sel_state.get(it.step, True)]
            st.session_state[extra_key] = existing + new_items
            st.success(f"{len(new_items)} items added to {auto_prog_label}. "
                       "They appear in the checklist after you generate the plan.")

    if st.button("Close preview", key="close_prev"):
        st.session_state.pop("preview_file", None)
        st.session_state.pop("preview_result", None)
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# STEP 1 — CONFIGURE
# ═════════════════════════════════════════════════════════════════════════════
def render_configure():
    _section("Étape 1 · Configurer le programme",
             "Renseignez le contexte ; le formulaire s'adapte au type de programme et à sa procédure Versigent.")

    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-label">Program Type</div>', unsafe_allow_html=True)
            prog_type = st.selectbox(
                "Select Program", options=list(PROGRAM_OPTIONS.keys()),
                format_func=lambda k: PROGRAM_OPTIONS[k], key="prog_types",
                label_visibility="collapsed")
        with c2:
            st.markdown('<div class="section-label">Customer</div>', unsafe_allow_html=True)
            _cust_opts = CUSTOMER_OPTIONS_NEW_PLANT if prog_type == "new_plant" else CUSTOMER_OPTIONS
            customer_key = st.selectbox(
                "Customer", options=list(_cust_opts.keys()),
                format_func=lambda k: _cust_opts[k], label_visibility="collapsed")

        customer = get_customer(customer_key)
        part_name = ""
        if prog_type in ("new", "transfer", "my_change", "capacity"):
            part_name = st.text_input("Part / Project Name",
                                      placeholder="e.g. Bracket Assembly X200")

        with st.expander(
            f"{customer['name']} — Requirements" if customer_key != "default"
            else "Plant Readiness — No customer confirmed yet", expanded=False):
            for req in customer["items"]:
                st.markdown(f"• {req}")

        with st.expander("Importer depuis une procédure (optionnel)", expanded=False):
            st.caption("Les checklists qualité intégrées sont toujours utilisées. "
                       "Déposez un fichier dans data/procedures/ pour en importer les étapes.")
            new_files = scan_new_files()
            if not new_files:
                st.markdown('<div class="file-miss">Aucun nouveau fichier détecté dans data/procedures/</div>',
                            unsafe_allow_html=True)
            for fp in new_files:
                prog_guess, confidence = auto_classify_file(fp)
                prog_label = _PROG_LABELS.get(prog_guess, "Unclassified")
                conf_pct = int(confidence * 100)
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(
                        '<div class="file-ok">'
                        f'<strong>{fp.name}</strong> → {prog_label}'
                        + (f' ({conf_pct}%)' if prog_guess != "unknown" else " — unrecognised")
                        + '</div>', unsafe_allow_html=True)
                with col_b:
                    if st.button("Preview", key=f"prev_{fp.name}"):
                        st.session_state["preview_file"] = str(fp)
                        st.session_state["preview_prog"] = prog_guess
                        st.session_state["preview_result"] = None
                        st.rerun()

    if not prog_type:
        st.info("Choisissez un type de programme pour afficher les champs.")
        return
    render_procedure_preview()

    inputs = {"customer_bonus": customer["score_bonus"],
              "customer_name": customer["name"], "customer": customer_key}
    primary_date = None
    meta = {}

    with st.container(border=True):
        primary_date, inputs, meta = _program_form(prog_type, inputs)

    st.markdown("<br>", unsafe_allow_html=True)
    nav1, nav2 = st.columns([3, 1])
    with nav2:
        gen = st.button("Générer le plan  →", type="primary", use_container_width=True)
    if gen:
        if not primary_date:
            st.error(f"Veuillez saisir la date « {_DATE_LABEL.get(prog_type, 'date')} » avant de générer.")
            return
        with st.spinner("Calcul du score de risque…"):
            result = calculate_score(prog_type, inputs)
        checklist, checklist_source = load_checklist(prog_type, context=inputs, return_source=True)
        extra_items = st.session_state.get(f"extra_items_{prog_type}", [])
        if extra_items:
            checklist = list(checklist) + extra_items
            checklist_source = checklist_source + f" + {len(extra_items)} from file"
        meta["sl_end_date"] = str(primary_date + timedelta(days=result.duration))
        st.session_state.update({
            "result": result, "checklist": checklist, "checklist_source": checklist_source,
            "stored_prog_type": prog_type,
            "part_name": part_name or prog_type.replace("_", " ").title(),
            "meta": meta, "customer_name": customer["name"], "inputs": inputs,
        })
        _goto(2)


def _program_form(prog_type, inputs):
    """Program-specific inputs. Returns (primary_date, inputs, meta).
    Widget keys, input keys and meta keys are preserved from the original app."""
    primary_date = None
    meta = {}

    if prog_type == "new":
        st.markdown('<div class="section-label">Key Dates</div>', unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        with d1: sop_date = st.date_input("SOP — Start of Production *", value=None)
        with d2: vff_date = st.date_input("VFF — Vehicle Functional Freeze", value=None)
        with d3: pre_date = st.date_input("Pre-Serial / Pilot Run", value=None)
        st.markdown('<div class="section-label">Team & Volume</div>', unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            headcount = st.number_input("Estimated Operators in Line", min_value=0, value=30,
                help="Number of direct operators required on this program at SOP")
        with t2:
            np_experience = st.selectbox("Team Experience with Customer / Product",
                ["known", "medium", "new"],
                format_func=lambda x: {"known": "Customer known — similar product experience",
                    "medium": "Medium experience — partial customer knowledge",
                    "new": "New customer / new product — no prior experience"}[x])
        st.markdown('<div class="section-label">Risk Factors</div>', unsafe_allow_html=True)
        pfmea = st.slider("PFMEA Highest Severity", 1, 10, 5)
        volume = st.number_input("Daily Volume at SOP (pcs/day)", min_value=0, value=2500)
        r1, r2 = st.columns(2)
        with r1:
            critical = st.radio("Special Characteristics", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Applied — SC identified" if x == "yes" else "Not applied")
        with r2:
            prod_sys = st.radio("Production System", ["batch", "ksk"], horizontal=True,
                format_func=lambda x: "Batch Production" if x == "batch" else "KSK System")
        _cat_lbl = {"AA": "Highest complexity", "A": "High", "B": "Medium", "C": "Low", "X": "Exempt"}
        proj_cat = st.selectbox("Project Category (Aptiv)", ["AA", "A", "B", "C", "X"], index=2,
            format_func=lambda x: f"{x} — {_cat_lbl[x]}")
        inputs.update({"pfmea": pfmea, "volume": volume, "critical": critical,
            "prod_system": prod_sys, "headcount": headcount, "np_experience": np_experience})
        primary_date = sop_date
        meta = {"primary_date": str(sop_date) if sop_date else "",
                "vff_date": str(vff_date) if vff_date else "",
                "pre_date": str(pre_date) if pre_date else "",
                "volume": volume, "proj_cat": proj_cat,
                "headcount": headcount, "np_experience": np_experience}

    elif prog_type == "transfer":
        st.markdown('<div class="section-label">Transfer Dates</div>', unsafe_allow_html=True)
        sop_date = st.date_input("Target SOP *", value=None)
        st.markdown('<div class="section-label">Transfer Context</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            recv_plant = st.selectbox("Receiving Plant Status", ["mature", "intermediate", "new"], index=1,
                format_func=lambda x: {"mature": "Mature — customer known",
                    "intermediate": "Intermediate — partial experience",
                    "new": "New — no customer history"}[x])
            eq_transfer = st.selectbox("Equipment Transfer Type", ["transfer", "duplicate", "new"],
                format_func=lambda x: {"transfer": "Same equipment transferred",
                    "duplicate": "Duplicate (new build, same design)",
                    "new": "New / different equipment"}[x])
            process_match = st.selectbox("Process Match", ["same", "similar", "different"],
                format_func=lambda x: {"same": "Same process & working practices",
                    "similar": "Similar — minor differences",
                    "different": "Different / new method"}[x])
        with c2:
            design_freeze = st.radio("Design Frozen During Transfer?", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Yes — frozen" if x == "yes" else "No — active changes")
            current_my = st.radio("Transfer Within Current MY?", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Yes — same MY" if x == "yes" else "No — new MY")
            safety_stock = st.radio("Safety Stock Built?", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Yes — buffer ready" if x == "yes" else "No / insufficient")
        st.markdown('<div class="section-label">Quality History at Source</div>', unsafe_allow_html=True)
        source_claims = st.selectbox("Open Claims at Source Plant", ["none", "low", "medium", "high"],
            format_func=lambda x: {"none": "None — clean quality history",
                "low": "1–3 open claims — minor issues",
                "medium": "4–10 open claims — active containment",
                "high": "> 10 claims or customer escalation"}[x])
        st.markdown('<div class="section-label">Risk Factors</div>', unsafe_allow_html=True)
        pfmea = st.slider("PFMEA Highest Severity", 1, 10, 5)
        f1, f2 = st.columns(2)
        with f1: st.number_input("PFMEA Highest RPN", 0, 1000, 200)
        with f2: volume = st.number_input("Transferred Volume (pcs/day)", 0, value=2500)
        r1, r2 = st.columns(2)
        with r1:
            critical = st.radio("Special Characteristics", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Applied" if x == "yes" else "Not applied")
        with r2:
            prod_sys = st.radio("Production System", ["batch", "ksk"], horizontal=True,
                format_func=lambda x: "Batch" if x == "batch" else "KSK")
        inputs.update({"recv_plant_status": recv_plant, "eq_transfer_type": eq_transfer,
            "design_freeze": design_freeze, "current_my": current_my,
            "safety_stock": safety_stock, "process_match": process_match,
            "source_claims": source_claims, "pfmea": pfmea, "volume": volume,
            "critical": critical, "prod_system": prod_sys})
        primary_date = sop_date
        meta = {"primary_date": str(sop_date) if sop_date else "", "volume": volume,
                "customer": inputs["customer"], "source_claims": source_claims}

    elif prog_type == "my_change":
        st.markdown('<div class="section-label">Implementation Date</div>', unsafe_allow_html=True)
        impl_date = st.date_input("Change Implementation Date *", value=None)
        st.markdown('<div class="section-label">Change Details</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            change_type = st.selectbox("Change Type", ["my", "design", "material", "process"],
                format_func=lambda x: {"my": "MY (Model Year) change",
                    "design": "Design change (drawing/spec)",
                    "material": "Material / supplier change", "process": "Process change"}[x])
            feas_status = st.selectbox("Feasibility Study", ["approved", "pending", "rejected"],
                format_func=lambda x: {"approved": "Approved — all YES",
                    "pending": "Pending review", "rejected": "Rejected — single NO found"}[x])
            eccl_stage = st.selectbox("ECCL Stage Reached", ["none", "preliminary", "interim", "final"],
                format_func=lambda x: {"none": "Not started", "preliminary": "Preliminary",
                    "interim": "Interim", "final": "Final"}[x])
        with c2:
            eo_costs = st.selectbox("Estimated E&O Costs", ["low", "medium", "high"],
                format_func=lambda x: {"low": "< 5,000 €", "medium": "5,000 – 50,000 €", "high": "> 50,000 €"}[x])
            multi_plant = st.radio("Multi-plant?", ["no", "yes"], horizontal=True,
                format_func=lambda x: "Single plant" if x == "no" else "Multiple plants")
            ksk_impact = st.radio("Affects KSK Modules?", ["no", "yes"], horizontal=True,
                format_func=lambda x: "No" if x == "no" else "Yes — PB2O update needed")
        st.markdown('<div class="section-label">Risk Factors</div>', unsafe_allow_html=True)
        pfmea = st.slider("PFMEA Severity", 1, 10, 5)
        critical = st.radio("Special Characteristics", ["yes", "no"], horizontal=True,
            format_func=lambda x: "Applied" if x == "yes" else "Not applied")
        eo_labels = {"low": "< 5k€", "medium": "5–50k€", "high": "> 50k€"}
        inputs.update({"feasibility_status": feas_status, "eccl_stage": eccl_stage,
            "eo_costs": eo_costs, "change_type": change_type, "multi_plant": multi_plant,
            "ksk_impact": ksk_impact, "pfmea": pfmea, "volume": 0, "critical": critical})
        primary_date = impl_date
        meta = {"primary_date": str(impl_date) if impl_date else "",
                "eccl_stage": eccl_stage.capitalize(), "eo_costs_label": eo_labels[eo_costs]}

    elif prog_type == "restart":
        st.markdown('<div class="section-label">Shutdown & Restart Dates</div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1: st.date_input("Shutdown Date", value=None)
        with d2: restart_date = st.date_input("Restart Date *", value=None)
        st.markdown('<div class="section-label">Shutdown Details</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            shutdown_dur = st.selectbox("Shutdown Duration", ["short", "medium", "long"], index=1,
                format_func=lambda x: {"short": "Short (≤ 1 week)", "medium": "Medium (2–3 weeks)", "long": "Long (≥ 4 weeks)"}[x])
            shutdown_type = st.selectbox("Shutdown Type", ["planned", "forced", "emergency"],
                format_func=lambda x: {"planned": "Planned (vacation, maintenance)",
                    "forced": "Forced (customer / supply / energy)", "emergency": "Emergency / unplanned"}[x])
            prep_status = st.selectbox("Shutdown Prep Checklist", ["complete", "partial", "missing"],
                format_func=lambda x: {"complete": "Completed before shutdown",
                    "partial": "Partially completed", "missing": "Not done"}[x])
        with c2:
            lpa_cov = st.selectbox("LPA per Area Before Release", ["planned", "partial", "none"],
                format_func=lambda x: {"planned": "Planned for all 3 areas",
                    "partial": "Some areas only", "none": "Not planned"}[x])
            abs_risk = st.selectbox("Absenteeism Risk on Restart", ["low", "medium", "high"],
                format_func=lambda x: {"low": "Low — full team expected",
                    "medium": "Medium — some absences", "high": "High — significant gaps"}[x])
            cont_team = st.radio("Contingency Response Team", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Defined" if x == "yes" else "Not defined")
        r1, r2 = st.columns(2)
        with r1:
            prod_sys = st.radio("Production System", ["batch", "ksk"], horizontal=True,
                format_func=lambda x: "Batch Production" if x == "batch" else "KSK System")
        with r2:
            critical = st.radio("Special Characteristics", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Applied" if x == "yes" else "Not applied")
        inputs.update({"shutdown_duration": shutdown_dur, "shutdown_type": shutdown_type,
            "prep_status": prep_status, "contingency_team": cont_team,
            "lpa_coverage": lpa_cov, "absenteeism_risk": abs_risk,
            "prod_system": prod_sys, "critical": critical})
        primary_date = restart_date
        dur_labels = {"short": "≤ 1 week", "medium": "2–3 weeks", "long": "≥ 4 weeks"}
        meta = {"primary_date": str(restart_date) if restart_date else "",
                "shutdown_duration": dur_labels[shutdown_dur],
                "shutdown_type": shutdown_type.capitalize(),
                "prep_status": prep_status.capitalize(),
                "lpa_coverage": {"planned": "All 3 areas", "partial": "Partial", "none": "Not planned"}[lpa_cov]}

    elif prog_type == "absence":
        st.markdown('<div class="section-label">Effective Date</div>', unsafe_allow_html=True)
        eff_date = st.date_input("Effective Date", value=None)
        st.markdown('<div class="section-label">Workforce Details</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            hc_current = st.number_input("Current Headcount", min_value=1, value=80)
            hc_affected = st.number_input("Affected Positions (gap)", min_value=0, value=15)
            volume = st.number_input("Daily Volume Impacted (pcs/day)", min_value=0, value=2000)
        with c2:
            turnover = st.slider("Turnover Rate (%)", 0, 100, 18)
            experience = st.radio("Remaining Team Experience", ["high", "low"], horizontal=True,
                format_func=lambda x: "Experienced" if x == "high" else "Low / New hires")
            critical = st.radio("Special Characteristics", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Applied" if x == "yes" else "Not applied")
        gap_pct = (hc_affected / max(1, hc_current)) * 100
        backup = math.ceil(hc_affected * 1.2)
        inputs.update({"hc_current": hc_current, "hc_affected": hc_affected,
            "turnover_pct": turnover, "experience": experience,
            "volume": volume, "critical": critical})
        primary_date = eff_date
        meta = {"primary_date": str(eff_date) if eff_date else "",
                "hc_gap_pct": gap_pct, "hc_affected": hc_affected,
                "turnover_pct": turnover, "backup_count": backup, "volume": volume}

    elif prog_type == "capacity":
        st.markdown('<div class="section-label">Capacity Change Date</div>', unsafe_allow_html=True)
        cap_date = st.date_input("Capacity Change Date *", value=None)
        st.markdown('<div class="section-label">Volume Change</div>', unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1: volume_cur = st.number_input("Current Daily Volume (pcs/day) *", min_value=0, value=2000)
        with v2: volume_new = st.number_input("Target Daily Volume (pcs/day) *", min_value=0, value=3000)
        with v3:
            if volume_cur > 0 and volume_new > 0:
                delta = (volume_new - volume_cur) / volume_cur * 100
                st.metric("Volume Change", f"{volume_new:,} pcs/day", delta=f"{delta:+.0f}%")
        st.markdown('<div class="section-label">Capacity Details</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            atv_status = st.selectbox("ATV — Authorized Tooling Volumes", ["approved", "pending", "missing"],
                format_func=lambda x: {"approved": "Approved by customer",
                    "pending": "Pending approval", "missing": "Not requested"}[x])
            cap_action = st.selectbox("Capacity Action Plan", ["overtime", "banking", "duplicate", "newline"],
                format_func=lambda x: {"overtime": "Overtime / extra shifts",
                    "banking": "Build & bank inventory", "duplicate": "Duplicate equipment / tools",
                    "newline": "Add new line / process"}[x])
        with c2:
            sys_change = st.radio("Manufacturing Flow Change?", ["no", "yes"], horizontal=True,
                format_func=lambda x: "No — same flow" if x == "no" else "Yes — PFMEA required")
            ruc_defined = st.radio("Ramp-Up Curve (RUC) Plan", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Defined" if x == "yes" else "Not defined")
            area_change = st.radio("Production Area Change?", ["no", "yes"], horizontal=True,
                format_func=lambda x: "No" if x == "no" else "Yes — area release needed")
        st.markdown('<div class="section-label">Risk Factors</div>', unsafe_allow_html=True)
        pfmea = st.slider("PFMEA Severity", 1, 10, 5) if sys_change == "yes" else 1
        r1, r2 = st.columns(2)
        with r1:
            critical = st.radio("Special Characteristics", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Applied" if x == "yes" else "Not applied")
        with r2:
            prod_sys = st.radio("Production System", ["batch", "ksk"], horizontal=True,
                format_func=lambda x: "Batch" if x == "batch" else "KSK")
        delta_pct = (volume_new - volume_cur) / max(1, volume_cur) * 100
        inputs.update({"volume_current": volume_cur, "volume_new": volume_new,
            "atv_status": atv_status, "sys_flow_change": sys_change,
            "capacity_action": cap_action, "ruc_defined": ruc_defined,
            "area_change": area_change, "pfmea": pfmea,
            "critical": critical, "prod_system": prod_sys})
        primary_date = cap_date
        meta = {"primary_date": str(cap_date) if cap_date else "",
                "volume": volume_cur, "volume_new": volume_new, "delta_pct_str": f"{delta_pct:+.0f}%"}

    elif prog_type == "new_plant":
        st.markdown('<div class="section-label">Key Dates</div>', unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        with d1: sop_date = st.date_input("SOP — Start of Production *", value=None)
        with d2: customer_visit = st.date_input("First Customer Visit (if known)", value=None)
        with d3: gp12_end = st.date_input("End of GP12 Period (if known)", value=None)
        st.markdown('<div class="section-label">Plant Profile</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            plant_type = st.selectbox("Plant Type", ["greenfield", "brownfield"],
                format_func=lambda x: {"greenfield": "Green Field — new site, no prior automotive history",
                    "brownfield": "Brown Field — existing site, new program added"}[x])
            it_readiness = st.selectbox("IT Tools Readiness (SAP, DCiX, CAO, APRISO, ALS...)",
                ["ready", "partial", "not_started"],
                format_func=lambda x: {"ready": "Ready — all systems validated",
                    "partial": "Partial — some tools missing or untested",
                    "not_started": "Not started — manual records in use"}[x])
            team_seniority = st.selectbox("Team Seniority / Capabilities", ["experienced", "mixed", "new"],
                format_func=lambda x: {"experienced": "Experienced — automotive background",
                    "mixed": "Mixed — some experienced, some new hires",
                    "new": "New hires — no prior wiring harness experience"}[x])
        with c2:
            mother_plant = st.radio("Mother / Sending Plant Identified?", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Yes — identified and engaged" if x == "yes" else "Not yet identified")
            qmp_done = st.radio("Quality Master Plan Reviewed?", ["yes", "partial", "no"], horizontal=True,
                format_func=lambda x: {"yes": "Done", "partial": "In progress", "no": "Not started"}[x])
            green_field_assess = st.radio("Green Field Assessment Performed?", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Yes — completed" if x == "yes" else "Not performed")
        st.markdown('<div class="section-label">Quality Readiness</div>', unsafe_allow_html=True)
        q1, q2 = st.columns(2)
        with q1:
            mother_issues_received = st.radio("Historic Quality Issues Received from Mother Plant?",
                ["yes", "no"], horizontal=True,
                format_func=lambda x: "Yes — received (8W before SOP)" if x == "yes" else "Not yet received")
        with q2:
            ppap_plan_ready = st.radio("PPAP Plan Defined (incl. R@R requirements)?", ["yes", "no"], horizontal=True,
                format_func=lambda x: "Yes — defined" if x == "yes" else "Not defined")
        st.markdown('<div class="section-label">Risk Factors</div>', unsafe_allow_html=True)
        pfmea = st.slider("PFMEA Highest Severity", 1, 10, 6)
        f1, f2 = st.columns(2)
        with f1: headcount = st.number_input("Estimated Quality Team Headcount", min_value=1, value=15)
        with f2: volume = st.number_input("Daily Volume at SOP (pcs/day)", min_value=0, value=1500)
        critical = st.radio("Special Characteristics", ["yes", "no"], horizontal=True,
            format_func=lambda x: "Applied" if x == "yes" else "Not applied")
        inputs.update({"plant_type": plant_type, "mother_plant": mother_plant,
            "it_readiness": it_readiness, "team_seniority": team_seniority, "qmp_done": qmp_done,
            "green_field_assess": green_field_assess, "mother_issues_received": mother_issues_received,
            "ppap_plan_ready": ppap_plan_ready, "pfmea": pfmea, "headcount": headcount,
            "volume": volume, "critical": critical})
        primary_date = sop_date
        meta = {"primary_date": str(sop_date) if sop_date else "",
                "customer_visit": str(customer_visit) if customer_visit else "TBD",
                "gp12_end": str(gp12_end) if gp12_end else "TBD",
                "plant_type": plant_type, "headcount": headcount, "volume": volume}

    return primary_date, inputs, meta


# ═════════════════════════════════════════════════════════════════════════════
# Shared helpers for dashboard / review
# ═════════════════════════════════════════════════════════════════════════════
def _parse_date(s):
    try:
        return date.fromisoformat(str(s)[:10])
    except (ValueError, TypeError):
        return None


def _readiness_counts(checklist):
    done = sum(1 for i in checklist if i.done)
    crit = sum(1 for i in checklist if i.critical and not i.done)
    todo = len(checklist) - done - crit
    return done, crit, todo


def _nav(prev_to=None, next_to=None, next_label="Suivant  →", prev_label="←  Précédent"):
    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, c3 = st.columns([1, 2, 1])
    with c1:
        if prev_to and st.button(prev_label, use_container_width=True, key=f"prev_{prev_to}"):
            _goto(prev_to)
    with c3:
        if next_to and st.button(next_label, type="primary", use_container_width=True, key=f"next_{next_to}"):
            _goto(next_to)


# ═════════════════════════════════════════════════════════════════════════════
# STEP 2 — DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
def render_dashboard():
    result = st.session_state["result"]
    checklist = st.session_state["checklist"]
    prog_type = st.session_state["stored_prog_type"]
    meta = st.session_state["meta"]
    cust_name = st.session_state["customer_name"]
    inputs = st.session_state.get("inputs", {})

    _section(f"Tableau de bord — {st.session_state['part_name']}",
             f"{PROGRAM_OPTIONS.get(prog_type, prog_type)} · {cust_name}")

    kpis = _build_kpis(prog_type, result, meta, cust_name)

    # ── Ligne 1 : Jauge | Recommandation ────────────────────────────────────
    c_gauge, c_reco = st.columns([1, 2])
    with c_gauge:
        with st.container(border=True):
            st.plotly_chart(
                charts.risk_gauge(result.score, result.risk, DARK, height=200),
                use_container_width=True, theme=None, config={"displayModeBar": False})
            st.markdown(
                f'<div style="text-align:center;margin-top:-14px;padding-bottom:6px;">'
                f'<span class="risk-badge" style="background:{RISK_COLORS[result.risk]}22;'
                f'color:{RISK_TEXT[result.risk]};">{result.risk} RISK</span></div>',
                unsafe_allow_html=True)
    with c_reco:
        pra_html = ""
        if getattr(result, "pra_forecast", ""):
            pc = {"GREEN": RISK_COLORS["LOW"], "YELLOW": RISK_COLORS["MEDIUM"],
                  "RED": RISK_COLORS["HIGH"]}.get(result.pra_forecast, "#64748B")
            pt = {"GREEN": RISK_TEXT["LOW"], "YELLOW": RISK_TEXT["MEDIUM"],
                  "RED": RISK_TEXT["HIGH"]}.get(result.pra_forecast, "#64748B")
            pra_html = (
                f'<div style="margin-top:12px;padding:8px 12px;background:{pc}22;'
                f'border-left:4px solid {pc};border-radius:6px;">'
                f'<span style="font-size:9px;letter-spacing:1.5px;color:{pt};'
                f'text-transform:uppercase;font-weight:700;">PRA Forecast</span> '
                f'<span style="font-weight:700;color:{pt};">{result.pra_forecast}</span>'
                f'<span style="color:var(--vg-muted);font-size:11px;"> · conformance ≈ {result.conformance}%</span></div>'
            )
        # Custom div: même style que st.container(border=True) + flex centrage vertical
        # min-height aligne sur la hauteur de la carte jauge (gauge 200px + badge + paddings ≈ 270px)
        st.markdown(
            '<div style="border:1px solid var(--vg-border);border-radius:16px;'
            'padding:20px 24px;background:var(--vg-surface);'
            'box-shadow:var(--vg-shadow-card);box-sizing:border-box;'
            'min-height:270px;display:flex;flex-direction:column;justify-content:center;">'
            '<div style="font-size:10px;letter-spacing:2px;color:var(--vg-accent-text);'
            'text-transform:uppercase;font-weight:700;margin-bottom:10px;">Recommandation</div>'
            f'<p style="color:var(--vg-fg);font-size:14px;line-height:1.65;margin:0;">'
            f'{result.recommendation}</p>'
            + pra_html + '</div>',
            unsafe_allow_html=True)

    # ── Ligne 2 : KPI strip (6 colonnes) ────────────────────────────────────
    kpi_cols = st.columns(len(kpis[:6]))
    for i, kpi in enumerate(kpis[:6]):
        with kpi_cols[i]:
            st.markdown(
                f'<div class="metric-card-kpi">'
                f'<div class="metric-label">{kpi["label"]}</div>'
                f'<div class="metric-value">{kpi["value"]}</div>'
                f'<div class="metric-sub">{kpi["sub"]}</div></div>',
                unsafe_allow_html=True)

    # ── Ligne 3 : Facteurs de risque | Donut checklist ───────────────────────
    c_factors, c_donut = st.columns([3, 2])
    with c_factors:
        with st.container(border=True):
            st.markdown('<div class="section-label">Facteurs de risque</div>',
                        unsafe_allow_html=True)
            if result.factors:
                st.plotly_chart(charts.factor_bar(result.factors, DARK),
                                use_container_width=True, theme=None,
                                config={"displayModeBar": False})
            else:
                st.caption("Aucun facteur détaillé pour ce type de programme.")
    with c_donut:
        done, crit, todo = _readiness_counts(checklist)
        with st.container(border=True):
            st.markdown('<div class="section-label">Composition checklist</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(
                charts.completion_donut(done, crit, todo, DARK,
                                        labels=("Déjà prêt", "Critique", "À traiter")),
                use_container_width=True, theme=None, config={"displayModeBar": False})

    # ── Ligne 4 : Timeline + Quality gates ───────────────────────────────────
    phases = get_phases(checklist) or ["All Items"]
    start = _parse_date(meta.get("primary_date"))
    end   = _parse_date(meta.get("sl_end_date"))
    fig_tl = charts.timeline(start, end, phases, DARK)
    if fig_tl is not None:
        with st.container(border=True):
            st.markdown(
                f'<div class="section-label">Fenêtre Safe Launch · '
                f'{start:%d %b %Y} → {end:%d %b %Y} ({result.duration} j)</div>',
                unsafe_allow_html=True)
            st.plotly_chart(fig_tl, use_container_width=True, theme=None,
                            config={"displayModeBar": False})

    cust  = get_customer(inputs.get("customer", "other"))
    gates = cust.get("gates", [])
    if gates:
        st.markdown(
            '<div class="section-label" style="margin-top:8px;">Quality Gates · '
            + cust.get("name", "") + '</div>'
            + '<div>' + "".join(
                f'<span class="vg-gate"><span class="dot"></span>{g}</span>'
                for g in gates) + '</div>',
            unsafe_allow_html=True)

    _nav(prev_to=1, next_to=3, next_label="Revue du plan  →")


# ═════════════════════════════════════════════════════════════════════════════
# STEP 3 — REVIEW
# ═════════════════════════════════════════════════════════════════════════════
def render_review():
    checklist = st.session_state["checklist"]
    prog_type = st.session_state["stored_prog_type"]

    _section("Étape 3 · Revue & affectation",
             "Cochez les items applicables, assignez un responsable et une échéance. "
             "Seuls les items cochés figureront dans les exports.")

    ck_key = f"review_{prog_type}_{len(checklist)}"
    if ck_key not in st.session_state:
        st.session_state[ck_key] = {item.step: {"checked": True, "owner": "", "due": None}
                                    for item in checklist}
    review_state = st.session_state[ck_key]

    review_phases = get_phases(checklist) or ["All Items"]

    # Filters
    with st.container(border=True):
        fc1, fc2, fc3 = st.columns([2, 1, 1])
        with fc1:
            phase_filter = st.selectbox("Filtrer par phase", ["Toutes les phases"] + review_phases)
        with fc2:
            only_critical = st.checkbox("Critiques uniquement")
        with fc3:
            only_unassigned = st.checkbox("Non assignés")

    def _visible(item):
        if phase_filter != "Toutes les phases" and (item.phase or "All Items") != phase_filter:
            return False
        if only_critical and not item.critical:
            return False
        if only_unassigned:
            s = review_state.get(item.step, {})
            if s.get("owner", "").strip() and s.get("due"):
                return False
        return True

    for phase in review_phases:
        phase_items = [i for i in checklist if (i.phase or "All Items") == phase]
        visible_items = [i for i in phase_items if _visible(i)]
        if not visible_items:
            continue
        checked_count = sum(1 for it in phase_items if review_state.get(it.step, {}).get("checked", True))

        ph_col1, ph_col2 = st.columns([5, 1])
        with ph_col1:
            st.markdown(
                f'<div class="review-phase-hdr"><span>{phase.upper()}</span>'
                f'<span class="review-count">{checked_count}/{len(phase_items)}</span></div>',
                unsafe_allow_html=True)
        with ph_col2:
            all_checked = all(review_state.get(it.step, {}).get("checked", True) for it in phase_items)
            if st.button("All" if not all_checked else "None", key=f"tog_{ck_key}_{phase}",
                         help=f"{'Select' if not all_checked else 'Deselect'} all in {phase}"):
                for it in phase_items:
                    if it.step in review_state:
                        review_state[it.step]["checked"] = not all_checked
                st.rerun()

        for item in visible_items:
            state = review_state.setdefault(item.step, {"checked": True, "owner": "", "due": None})
            bdr = "var(--vg-risk-high)" if item.critical else "var(--vg-border)"
            bg = "var(--vg-risk-high-bg)" if item.critical else "var(--vg-surface-alt)"
            st.markdown(f'<div style="border-left:3px solid {bdr};background:{bg};'
                        'border-radius:4px;padding:4px 0 4px 10px;margin:3px 0;">',
                        unsafe_allow_html=True)
            row_cols = st.columns([0.4, 4.5, 2.5, 2.0])
            with row_cols[0]:
                checked = st.checkbox("✓", value=state["checked"], key=f"chk_{ck_key}_{item.step}",
                                      label_visibility="collapsed")
                state["checked"] = checked
            with row_cols[1]:
                crit_badge = " 🔴" if item.critical else ""
                tcolor = "var(--vg-risk-high-text)" if item.critical else "var(--vg-fg)"
                st.markdown(
                    f'<div style="font-size:12px;color:{tcolor};padding-top:6px;opacity:{"1" if checked else "0.38"};">'
                    f'<strong style="font-family:monospace;color:var(--vg-accent-text);font-size:10px;">{item.step}</strong>'
                    f'&nbsp;&nbsp;{item.text}{crit_badge}</div>', unsafe_allow_html=True)
            if checked:
                with row_cols[2]:
                    state["owner"] = st.text_input("Owner", value=state["owner"],
                        placeholder="e.g. J. Martin", key=f"own_{ck_key}_{item.step}",
                        label_visibility="collapsed")
                with row_cols[3]:
                    state["due"] = st.date_input("Due date", value=state["due"],
                        key=f"due_{ck_key}_{item.step}", label_visibility="collapsed",
                        format="DD/MM/YYYY")
            else:
                with row_cols[2]:
                    st.markdown('<div style="height:36px;"></div>', unsafe_allow_html=True)
                with row_cols[3]:
                    st.markdown('<div style="height:36px;"></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Live progress
    total = len(checklist)
    selected = sum(1 for s in review_state.values() if s.get("checked", True))
    assigned = sum(1 for s in review_state.values()
                   if s.get("checked") and s.get("owner", "").strip() and s.get("due"))
    selected_only = selected - assigned
    excluded = total - selected

    st.markdown("<br>", unsafe_allow_html=True)
    p1, p2 = st.columns([1, 1.3])
    with p1:
        _section("Avancement de la revue")
        with st.container(border=True):
            st.plotly_chart(charts.completion_donut(assigned, selected_only, excluded, DARK,
                            labels=("Assigné (owner+date)", "Sélectionné", "Exclu")),
                            use_container_width=True, theme=None, config={"displayModeBar": False})
    with p2:
        _section("Sélection par phase")
        rows = [(ph, sum(1 for i in checklist if (i.phase or "All Items") == ph
                         and review_state.get(i.step, {}).get("checked", True)),
                 sum(1 for i in checklist if (i.phase or "All Items") == ph))
                for ph in review_phases]
        with st.container(border=True):
            st.plotly_chart(charts.phase_bars(rows, DARK),
                            use_container_width=True, theme=None, config={"displayModeBar": False})
        m1, m2, m3 = st.columns(3)
        m1.metric("Sélectionnés", f"{selected}/{total}")
        m2.metric("Avec responsable + date", assigned)
        m3.metric("Exclus", excluded)

    _nav(prev_to=2, next_to=4, next_label="Aller à l'export  →")


# ═════════════════════════════════════════════════════════════════════════════
# STEP 4 — EXPORT
# ═════════════════════════════════════════════════════════════════════════════
def render_export():
    result = st.session_state["result"]
    checklist = st.session_state["checklist"]
    prog_type = st.session_state["stored_prog_type"]
    part_name = st.session_state["part_name"]
    meta = st.session_state["meta"]
    cust_name = st.session_state["customer_name"]
    checklist_source = st.session_state.get("checklist_source", "built-in")

    ck_key = f"review_{prog_type}_{len(checklist)}"
    review_state = st.session_state.get(ck_key, {})

    _section("Étape 4 · Export", "Vérifiez le récapitulatif puis téléchargez les livrables brandés.")

    import copy as _copy
    reviewed_checklist = []
    for item in checklist:
        state = review_state.get(item.step, {})
        if state.get("checked", True):
            r = _copy.copy(item)
            r.done = item.done
            r.owner = state.get("owner", "").strip()
            r.due = str(state["due"]) if state.get("due") else ""
            reviewed_checklist.append(r)

    selected_items = len(reviewed_checklist)
    with_owner = sum(1 for i in reviewed_checklist if i.owner)
    with_date = sum(1 for i in reviewed_checklist if i.due)

    # Recap
    with st.container(border=True):
        rc = st.columns(4)
        rc[0].metric("Risque", f"{result.risk} · {result.score}/100")
        rc[1].metric("Items retenus", f"{selected_items}/{len(checklist)}")
        rc[2].metric("Avec responsable", with_owner)
        rc[3].metric("Avec échéance", with_date)
        st.caption(f"{PROGRAM_OPTIONS.get(prog_type, prog_type)} · {part_name} · {cust_name} · source : {checklist_source}")

    # Export previews
    pv1, pv2 = st.columns(2)
    with pv1:
        with st.container(border=True):
            st.markdown('<div class="vg-section-title">PowerPoint</div>'
                        '<div class="vg-section-sub">Présentation brandée Versigent</div>', unsafe_allow_html=True)
            for s in ["Cover — risque & KPIs", "Analyse de risque", "Facteurs de risque",
                      "Vue 4 colonnes par phase", "Slides détaillées par phase"]:
                st.markdown(f"• {s}")
    with pv2:
        with st.container(border=True):
            st.markdown('<div class="vg-section-title">Excel</div>'
                        '<div class="vg-section-sub">Classeur de suivi</div>', unsafe_allow_html=True)
            for s in ["Summary", "Risk Factors", "Checklist", "Plan (transposé)", "Gantt"]:
                st.markdown(f"• {s}")

    st.markdown("<br>", unsafe_allow_html=True)
    if selected_items == 0:
        st.warning("Aucun item sélectionné — revenez à l'étape Revue et cochez au moins un item.")
    else:
        safe_name = (part_name or prog_type).replace(" ", "_").replace("/", "_")
        d1, d2, d3 = st.columns(3)
        with d1:
            ppt_bytes = generate_ppt(prog_type, part_name or prog_type, result,
                                     reviewed_checklist, meta, cust_name)
            st.download_button("⬇ PowerPoint", data=ppt_bytes,
                file_name=f"Versigent_{safe_name}_SafeLaunch.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True)
        with d2:
            xl_bytes = generate_excel(prog_type, part_name or prog_type, result,
                                      reviewed_checklist, meta, cust_name)
            st.download_button("⬇ Excel", data=xl_bytes,
                file_name=f"Versigent_{safe_name}_SafeLaunch.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with d3:
            plan_data = {"timestamp": str(datetime.now()), "prog_type": prog_type,
                         "part_name": part_name, "customer": cust_name,
                         "score": result.score, "risk": result.risk,
                         "inputs": st.session_state.get("inputs", {}), "meta": meta,
                         "checklist_source": checklist_source,
                         "reviewed_items": [{"step": i.step, "text": i.text, "phase": i.phase,
                                             "owner": i.owner, "due": i.due, "critical": i.critical}
                                            for i in reviewed_checklist]}
            st.download_button("⬇ Plan (JSON)",
                data=json.dumps(plan_data, indent=2, default=str).encode("utf-8"),
                file_name=f"Versigent_{safe_name}_Plan.json",
                mime="application/json", use_container_width=True)

    _nav(prev_to=3, next_to=None)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN DISPATCH
# ═════════════════════════════════════════════════════════════════════════════
render_topbar()

# Guard: steps 2-4 require a generated plan
step = st.session_state["step"]
if step > 1 and "result" not in st.session_state:
    step = st.session_state["step"] = 1

# Scroll to top when the active step changes (Streamlit 1.35 doesn't auto-scroll)
if st.session_state.get("_prev_step") != step:
    st.session_state["_prev_step"] = step
    components.html(
        "<script>parent.document.querySelector('section.main')"
        ".scrollTo({top:0,behavior:'instant'})</script>",
        height=0,
    )

render_stepper(step)

if step == 1:
    render_configure()
elif step == 2:
    render_dashboard()
elif step == 3:
    render_review()
elif step == 4:
    render_export()

render_tabbar(step, "result" in st.session_state)
