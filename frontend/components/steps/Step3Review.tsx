"use client"
import { useState } from "react"
import { ChecklistItem, WizardState } from "@/lib/types"
import { ArrowLeft, ArrowRight, CheckCircle2, AlertCircle, Circle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface Props {
  state: WizardState
  onChange: (partial: Partial<WizardState>) => void
  onPrev: () => void
  onNext: () => void
}

function groupByPhase(items: ChecklistItem[]) {
  const groups: Record<string, ChecklistItem[]> = {}
  for (const item of items) {
    if (!groups[item.phase]) groups[item.phase] = []
    groups[item.phase].push(item)
  }
  return groups
}

export function Step3Review({ state, onChange, onPrev, onNext }: Props) {
  const [filter, setFilter] = useState<"all" | "critical" | "unassigned">("all")

  const updateItem = (idx: number, patch: Partial<ChecklistItem>) => {
    const next = state.checklist.map((it, i) => i === idx ? { ...it, ...patch } : it)
    onChange({ checklist: next })
  }

  const filtered = state.checklist.filter(it => {
    if (filter === "critical") return it.critical
    if (filter === "unassigned") return !it.owner
    return true
  })

  const groups = groupByPhase(filtered)
  const doneCount = state.checklist.filter(i => i.selected !== false).length
  const total = state.checklist.length

  return (
    <div className="pb-6">
      <div className="mb-5">
        <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display, sans-serif)" }}>
          Étape 3 · Revue & affectation
        </h1>
        <p className="text-sm mt-0.5" style={{ color: "var(--vg-muted)" }}>
          Cochez les items, assignez un responsable et une échéance.
        </p>
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap gap-2 mb-4">
        {[["all", "Tous"], ["critical", "Critiques"], ["unassigned", "Non assignés"]].map(([v, l]) => (
          <button key={v} onClick={() => setFilter(v as typeof filter)}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all"
            style={{
              background: filter === v ? "var(--vg-fg)" : "var(--vg-surface)",
              color: filter === v ? "white" : "var(--vg-muted)",
              border: "1px solid var(--vg-border)",
            }}>
            {l}
          </button>
        ))}
        <span className="ml-auto text-xs self-center" style={{ color: "var(--vg-muted)" }}>
          {doneCount}/{total} sélectionnés
        </span>
      </div>

      {/* Checklist by phase */}
      <div className="space-y-4">
        {Object.entries(groups).map(([phase, items]) => (
          <div key={phase}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] font-bold uppercase tracking-[2px]" style={{ color: "var(--vg-accent)" }}>{phase}</span>
              <div className="flex-1 h-px" style={{ background: "var(--vg-border)" }} />
              <span className="text-[10px]" style={{ color: "var(--vg-muted)" }}>{items.length}</span>
            </div>
            <div className="rounded-2xl overflow-hidden" style={{ background: "var(--vg-surface)", border: "1px solid var(--vg-border)", boxShadow: "var(--vg-shadow-card)" }}>
              {items.map((item, relIdx) => {
                const absIdx = state.checklist.findIndex(i => i.step === item.step && i.text === item.text)
                const selected = item.selected !== false
                return (
                  <div key={item.step}
                    className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 py-3 transition-colors"
                    style={{
                      borderBottom: relIdx < items.length - 1 ? "1px solid var(--vg-border)" : "none",
                      background: selected ? "transparent" : "var(--vg-surface-alt)",
                      opacity: selected ? 1 : 0.6,
                    }}>

                    {/* Checkbox + step badge */}
                    <div className="flex items-center gap-3 shrink-0">
                      <button onClick={() => updateItem(absIdx, { selected: !selected })} className="transition-all">
                        {selected
                          ? <CheckCircle2 className="w-5 h-5" style={{ color: "var(--vg-accent)" }} />
                          : <Circle className="w-5 h-5" style={{ color: "var(--vg-border)" }} />
                        }
                      </button>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{ background: item.critical ? "var(--vg-risk-high-bg)" : "var(--vg-surface-alt)", color: item.critical ? "var(--vg-risk-high)" : "var(--vg-muted)" }}>
                        {item.step}
                      </span>
                      {item.critical && <AlertCircle className="w-3.5 h-3.5" style={{ color: "var(--vg-risk-high)" }} />}
                    </div>

                    {/* Text */}
                    <p className="flex-1 text-sm leading-snug" style={{ color: "var(--vg-fg)" }}>{item.text}</p>

                    {/* Owner + Date */}
                    <div className="flex gap-2 shrink-0">
                      <input type="text" placeholder="Responsable"
                        className="text-xs rounded-xl px-3 py-1.5 w-28 outline-none"
                        style={{ background: "var(--vg-surface-alt)", border: "1px solid var(--vg-border)", color: "var(--vg-fg)" }}
                        value={item.owner} onChange={e => updateItem(absIdx, { owner: e.target.value })} />
                      <input type="date"
                        className="text-xs rounded-xl px-3 py-1.5 outline-none"
                        style={{ background: "var(--vg-surface-alt)", border: "1px solid var(--vg-border)", color: "var(--vg-fg)" }}
                        value={item.due} onChange={e => updateItem(absIdx, { due: e.target.value })} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mt-5">
        <button onClick={onPrev} className="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl text-sm font-semibold" style={{ background: "var(--vg-surface-alt)", color: "var(--vg-fg)", border: "1px solid var(--vg-border)" }}>
          <ArrowLeft className="w-4 h-4" /> Précédent
        </button>
        <button onClick={onNext} className="flex-1 flex items-center justify-center gap-2 py-3 rounded-2xl text-sm font-bold" style={{ background: "var(--vg-accent)", color: "white", boxShadow: "0 4px 16px rgba(205,121,37,0.3)" }}>
          Exporter <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
