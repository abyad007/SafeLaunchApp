"use client"
import { ScoreResult, ChecklistItem, WizardState } from "@/lib/types"
import { ArrowLeft, ArrowRight } from "lucide-react"
import { RadialBarChart, RadialBar, Cell, PieChart, Pie, Tooltip, BarChart, Bar, XAxis, Cell as RCell, ResponsiveContainer } from "recharts"

const RISK_COLOR = { HIGH: "#DC2626", MEDIUM: "#D97706", LOW: "#16A34A" }
const RISK_BG    = { HIGH: "#FFF0EE", MEDIUM: "#FFF7ED", LOW: "#F0FFF4" }

function RiskGauge({ score, risk }: { score: number; risk: "LOW"|"MEDIUM"|"HIGH" }) {
  const c = RISK_COLOR[risk]
  const data = [{ value: score }, { value: 100 - score }]
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative">
        <PieChart width={220} height={130}>
          <Pie data={data} startAngle={180} endAngle={0} cx="50%" cy="100%" outerRadius={100} innerRadius={66} dataKey="value" stroke="none">
            <Cell fill={c} opacity={0.9} />
            <Cell fill="var(--vg-border)" />
          </Pie>
        </PieChart>
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-2">
          <span className="text-4xl font-black" style={{ fontFamily: "var(--font-display, sans-serif)", color: c }}>{score}</span>
          <span className="text-xs" style={{ color: "var(--vg-muted)" }}>/100</span>
        </div>
      </div>
      <span className="mt-1 px-4 py-1 rounded-full text-sm font-bold" style={{ background: RISK_BG[risk], color: c }}>
        {risk} RISK
      </span>
    </div>
  )
}

function KpiCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="rounded-2xl p-3 flex flex-col gap-0.5" style={{ background: "var(--vg-surface)", border: "1px solid var(--vg-border)", boxShadow: "var(--vg-shadow-card)" }}>
      <span className="text-[9px] font-bold uppercase tracking-widest" style={{ color: "var(--vg-muted)" }}>{label}</span>
      <span className="text-lg font-black leading-tight truncate" style={{ fontFamily: "var(--font-display, sans-serif)", color: "var(--vg-fg)" }}>{value}</span>
      {sub && <span className="text-[10px]" style={{ color: "var(--vg-muted)" }}>{sub}</span>}
    </div>
  )
}

function FactorBars({ factors }: { factors: ScoreResult["factors"] }) {
  const sorted = [...factors].sort((a, b) => b.percent - a.percent)
  return (
    <ResponsiveContainer width="100%" height={Math.max(160, sorted.length * 34)}>
      <BarChart data={sorted} layout="vertical" margin={{ left: 0, right: 40, top: 0, bottom: 0 }}>
        <XAxis type="number" domain={[0, 100]} hide />
        <Tooltip formatter={(v) => [`${v}%`]} />
        <Bar dataKey="percent" radius={[0, 4, 4, 0]}>
          {sorted.map((f, i) => <RCell key={i} fill="var(--vg-fg)" opacity={0.75 - i * 0.1} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

function CompletionDonut({ items }: { items: ChecklistItem[] }) {
  const done = items.filter(i => i.done).length
  const critical = items.filter(i => !i.done && i.critical).length
  const todo = items.length - done - critical
  const pct = items.length ? Math.round(done / items.length * 100) : 0
  const data = [
    { name: "Fait", value: done, fill: "#16A34A" },
    { name: "Critique", value: critical, fill: "#DC2626" },
    { name: "À traiter", value: todo, fill: "var(--vg-border)" },
  ]
  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <PieChart width={160} height={160}>
          <Pie data={data} cx="50%" cy="50%" outerRadius={72} innerRadius={48} dataKey="value" stroke="none">
            {data.map((d, i) => <Cell key={i} fill={d.fill} />)}
          </Pie>
          <Tooltip />
        </PieChart>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-black" style={{ fontFamily: "var(--font-display, sans-serif)", color: "var(--vg-fg)" }}>{pct}%</span>
          <span className="text-[10px]" style={{ color: "var(--vg-muted)" }}>fait</span>
        </div>
      </div>
      <div className="flex gap-3 text-[10px]" style={{ color: "var(--vg-muted)" }}>
        {data.map(d => <span key={d.name} className="flex items-center gap-1"><span className="w-2 h-2 rounded-full inline-block" style={{ background: d.fill }} />{d.name}: {d.value}</span>)}
      </div>
    </div>
  )
}

interface Props {
  state: WizardState
  onPrev: () => void
  onNext: () => void
}

export function Step2Dashboard({ state, onPrev, onNext }: Props) {
  const r = state.result!
  const kpis = [
    { label: "Risk Score",      value: `${r.score}/100`,   sub: "Niveau de risque" },
    { label: "Safe Launch",     value: r.duration ? `${r.duration} j` : "GP12", sub: "Fenêtre post-SOP" },
    { label: "Projected FPY",   value: r.fpy,              sub: "First Pass Yield" },
    { label: "Inspection",      value: r.inspection.split(" ")[0] + " " + (r.inspection.split(" ")[1] ?? ""), sub: "Méthode contrôle" },
    { label: "PPAP Level",      value: r.ppap,             sub: "Soumission client" },
    { label: "SL Window End",   value: state.meta.primary_date ? new Date(new Date(state.meta.primary_date).getTime() + r.duration * 86400000).toLocaleDateString("fr-FR") : "—", sub: "Fin safe launch" },
  ]

  return (
    <div className="pb-6">
      <div className="mb-5">
        <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display, sans-serif)" }}>
          Tableau de bord — {state.partName}
        </h1>
        <p className="text-xs mt-0.5" style={{ color: "var(--vg-accent-text)" }}>
          {state.progType} · {state.customer}
        </p>
      </div>

      {/* Row 1: Gauge + Recommendation */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 mb-4">
        <div className="sm:col-span-2 rounded-2xl p-5 flex flex-col items-center justify-center" style={{ background: "var(--vg-surface)", border: "1px solid var(--vg-border)", boxShadow: "var(--vg-shadow-card)" }}>
          <RiskGauge score={r.score} risk={r.risk as any} />
        </div>
        <div className="sm:col-span-3 rounded-2xl p-5 flex flex-col justify-center" style={{ background: "var(--vg-surface)", border: "1px solid var(--vg-border)", boxShadow: "var(--vg-shadow-card)" }}>
          <p className="text-[10px] font-bold uppercase tracking-widest mb-2" style={{ color: "var(--vg-accent)" }}>Recommandation</p>
          <p className="text-sm leading-relaxed" style={{ color: "var(--vg-fg)" }}>{r.recommendation}</p>
          {r.pra_forecast && (
            <span className="mt-3 inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full self-start"
              style={{ background: r.pra_forecast === "GREEN" ? "#F0FFF4" : "#FFF0EE", color: r.pra_forecast === "GREEN" ? "#15803D" : "#B91C1C" }}>
              PRA: {r.pra_forecast} · {r.conformance}% conformité
            </span>
          )}
        </div>
      </div>

      {/* Row 2: KPI Strip */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 mb-4">
        {kpis.map(k => <KpiCard key={k.label} {...k} />)}
      </div>

      {/* Row 3: Factor bars + Donut */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 mb-4">
        <div className="sm:col-span-3 rounded-2xl p-5" style={{ background: "var(--vg-surface)", border: "1px solid var(--vg-border)", boxShadow: "var(--vg-shadow-card)" }}>
          <p className="text-[10px] font-bold uppercase tracking-widest mb-3" style={{ color: "var(--vg-muted)" }}>Facteurs de risque</p>
          <div className="space-y-2">
            {[...r.factors].sort((a, b) => b.percent - a.percent).map(f => (
              <div key={f.name}>
                <div className="flex justify-between text-xs mb-0.5" style={{ color: "var(--vg-fg)" }}>
                  <span>{f.name}</span>
                  <span style={{ color: "var(--vg-muted)" }}>{f.value}/{f.max}</span>
                </div>
                <div className="h-2 rounded-full overflow-hidden" style={{ background: "var(--vg-border)" }}>
                  <div className="h-full rounded-full transition-all" style={{ width: `${f.percent}%`, background: "var(--vg-fg)" }} />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="sm:col-span-2 rounded-2xl p-5 flex flex-col items-center justify-center" style={{ background: "var(--vg-surface)", border: "1px solid var(--vg-border)", boxShadow: "var(--vg-shadow-card)" }}>
          <p className="text-[10px] font-bold uppercase tracking-widest mb-3 self-start" style={{ color: "var(--vg-muted)" }}>Composition checklist</p>
          <CompletionDonut items={state.checklist} />
        </div>
      </div>

      {/* Nav buttons */}
      <div className="flex gap-3">
        <button onClick={onPrev} className="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl text-sm font-semibold transition-colors" style={{ background: "var(--vg-surface-alt)", color: "var(--vg-fg)", border: "1px solid var(--vg-border)" }}>
          <ArrowLeft className="w-4 h-4" /> Précédent
        </button>
        <button onClick={onNext} className="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl text-sm font-bold transition-all" style={{ background: "var(--vg-accent)", color: "white", boxShadow: "0 4px 16px rgba(205,121,37,0.3)" }}>
          Revue du plan <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
