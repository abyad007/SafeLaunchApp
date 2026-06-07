# core/charts.py
# ─────────────────────────────────────────────────────────────────────────────
# Interactive Plotly figures for the Safe Launch dashboard.
# All colors come from the design system (core.theme.color) and honor dark mode.
# Figures are transparent so they sit on the app's light/dark surfaces.
# Render with: st.plotly_chart(fig, use_container_width=True, theme=None,
#                              config={"displayModeBar": False})
# ─────────────────────────────────────────────────────────────────────────────

from datetime import timedelta

import plotly.graph_objects as go

from core.theme import color

_DISPLAY = "Barlow Condensed, sans-serif"
_BODY    = "Barlow, sans-serif"


def _base(fig, dark, height, top=28):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=top, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=_BODY, color=color("foreground", dark), size=12),
        hoverlabel=dict(font=dict(family=_BODY)),
    )
    return fig


def _risk_color(risk, dark):
    return {
        "HIGH":   color("risk-high", dark),
        "MEDIUM": color("risk-medium", dark),
        "LOW":    color("risk-low", dark),
    }.get(risk, color("muted-foreground", dark))


# ── 1. Risk gauge ────────────────────────────────────────────────────────────
def risk_gauge(score, risk, dark=False, height=230):
    c = _risk_color(risk, dark)
    num_size = 32 if height < 220 else 38
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": " /100",
                "font": {"size": num_size, "color": c, "family": _DISPLAY}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1,
                     "tickcolor": color("muted-foreground", dark)},
            "bar": {"color": c, "thickness": 0.30},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 33],  "color": color("risk-low-bg", dark)},
                {"range": [33, 66], "color": color("risk-medium-bg", dark)},
                {"range": [66, 100], "color": color("risk-high-bg", dark)},
            ],
            "threshold": {"line": {"color": c, "width": 4},
                          "thickness": 0.85, "value": score},
        },
    ))
    return _base(fig, dark, height, top=10)


# ── 2. Risk factor breakdown (horizontal bars, sorted) ───────────────────────
def factor_bar(factors, dark=False):
    items = sorted(
        factors,
        key=lambda f: (f.value / f.max if getattr(f, "max", 0) else 0),
        reverse=True,
    )
    names = [f.name for f in items]
    pct   = [round((f.value / f.max * 100) if f.max else 0) for f in items]
    txt   = [f"{f.value}/{f.max}" for f in items]
    fig = go.Figure(go.Bar(
        x=pct, y=names, orientation="h",
        marker_color=color("foreground", dark),
        text=txt, textposition="auto",
        textfont=dict(color=color("background", dark)),
        cliponaxis=False,
        hovertemplate="%{y}<br>%{x}% of max<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 100], ticksuffix="%",
                   gridcolor=color("border", dark), zeroline=False),
        yaxis=dict(autorange="reversed", automargin=True),
        bargap=0.35,
    )
    return _base(fig, dark, max(190, 34 * len(items) + 60))


# ── 3. Completion donut (done / critical pending / to do) ────────────────────
def completion_donut(done, critical, todo, dark=False,
                     labels=("Done", "Critical pending", "To do")):
    total = done + critical + todo
    pct = round(done / total * 100) if total else 0
    fig = go.Figure(go.Pie(
        labels=list(labels),
        values=[done, critical, todo],
        hole=0.64,
        sort=False,
        direction="clockwise",
        marker_colors=[color("risk-low", dark),
                       color("risk-high", dark),
                       color("border", dark)],
        textinfo="value",
        hovertemplate="%{label}: %{value}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, x=0.5, xanchor="center"),
        annotations=[dict(text=f"<b>{pct}%</b><br>done", showarrow=False,
                          font=dict(family=_DISPLAY, size=22,
                                    color=color("foreground", dark)))],
    )
    return _base(fig, dark, 260)


# ── 4. Per-phase progress (stacked horizontal bars) ──────────────────────────
def phase_bars(rows, dark=False):
    """rows: list of (phase_name, done_count, total_count)."""
    phases = [r[0] for r in rows]
    done   = [r[1] for r in rows]
    rem    = [max(0, r[2] - r[1]) for r in rows]
    fig = go.Figure()
    fig.add_bar(y=phases, x=done, orientation="h", name="Selected/Done",
                marker_color=color("foreground", dark),
                hovertemplate="%{y}<br>Done: %{x}<extra></extra>")
    fig.add_bar(y=phases, x=rem, orientation="h", name="Remaining",
                marker_color=color("border", dark),
                hovertemplate="%{y}<br>Remaining: %{x}<extra></extra>")
    fig.update_layout(
        barmode="stack",
        yaxis=dict(autorange="reversed", automargin=True),
        xaxis=dict(gridcolor=color("border", dark), zeroline=False, dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0.5, xanchor="center"),
        bargap=0.4,
    )
    return _base(fig, dark, max(170, 42 * len(rows) + 70))


# ── 5. Safe-launch timeline (phase bands across the window) ───────────────────
def timeline(start, end, phases, dark=False):
    """start, end: datetime.date. phases: ordered list of phase names.
    Splits the [start, end] window into sequential phase bands. Returns None
    if inputs are insufficient."""
    if not start or not end or not phases or end <= start:
        return None

    span = (end - start).days
    n = len(phases)
    seg = max(1, span // n)

    palette = [
        color("foreground", dark),
        color("accent", dark),
        color("risk-low", dark),
        color("muted-foreground", dark),
        color("risk-medium", dark),
    ]

    fig = go.Figure()
    cur = start
    for i, ph in enumerate(phases):
        seg_end = end if i == n - 1 else min(end, cur + timedelta(days=seg))
        fig.add_trace(go.Bar(
            y=[ph], x=[(seg_end - cur).days * 86_400_000],  # width in ms
            base=cur, orientation="h",
            marker_color=palette[i % len(palette)],
            marker_line_width=0,
            hovertemplate=f"{ph}<br>{cur:%d %b} → {seg_end:%d %b}<extra></extra>",
            showlegend=False,
        ))
        cur = seg_end

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(type="date", gridcolor=color("border", dark),
                   tickformat="%d %b", zeroline=False),
        yaxis=dict(autorange="reversed", automargin=True),
        bargap=0.45,
    )
    # SOP marker line at the start
    fig.add_vline(x=start, line_width=2, line_dash="dot",
                  line_color=color("accent", dark))
    return _base(fig, dark, max(160, 40 * n + 70))
