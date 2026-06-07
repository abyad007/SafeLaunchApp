"use client"
import { useState } from "react"
import { WizardState } from "@/lib/types"
import { api } from "@/lib/api"
import { ArrowLeft, Download, Loader2, FileText, Table, FileJson } from "lucide-react"

interface Props {
  state: WizardState
  onPrev: () => void
}

function download(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url; a.download = name; a.click()
  URL.revokeObjectURL(url)
}

function buildPayload(state: WizardState) {
  return {
    prog_type: state.progType,
    part_name: state.partName,
    customer_name: state.customer,
    result: state.result,
    checklist: state.checklist.filter(i => i.selected !== false),
    meta: state.meta,
  }
}

export function Step4Export({ state, onPrev }: Props) {
  const [loading, setLoading] = useState<string | null>(null)
  const [done, setDone] = useState<string[]>([])

  const handle = async (format: "ppt" | "excel" | "json") => {
    setLoading(format)
    try {
      if (format === "json") {
        const payload = buildPayload(state)
        const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" })
        download(blob, `Versigent_${state.partName.replace(/ /g, "_")}_Plan.json`)
      } else {
        const blob = format === "ppt"
          ? await api.exportPpt(buildPayload(state))
          : await api.exportExcel(buildPayload(state))
        const ext = format === "ppt" ? "pptx" : "xlsx"
        download(blob, `Versigent_${state.partName.replace(/ /g, "_")}_SafeLaunch.${ext}`)
      }
      setDone(d => [...d, format])
    } catch (e) {
      alert("Erreur export: " + (e as Error).message)
    } finally {
      setLoading(null)
    }
  }

  const exports = [
    { key: "ppt",   label: "PowerPoint",  sub: "Présentation Versigent branding",  Icon: FileText,  ext: ".pptx" },
    { key: "excel", label: "Excel",        sub: "Plan détaillé + Gantt chart",       Icon: Table,     ext: ".xlsx" },
    { key: "json",  label: "JSON",         sub: "Données brutes pour intégration",   Icon: FileJson,  ext: ".json" },
  ] as const

  return (
    <div className="pb-6 max-w-lg mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold" style={{ fontFamily: "var(--font-display, sans-serif)" }}>
          Étape 4 · Export
        </h1>
        <p className="text-sm mt-0.5" style={{ color: "var(--vg-muted)" }}>
          Téléchargez votre plan de lancement sécurisé.
        </p>
      </div>

      {/* Summary card */}
      <div className="rounded-2xl p-5 mb-6" style={{ background: "var(--vg-surface)", border: "2px solid var(--vg-accent)", boxShadow: "0 4px 20px rgba(205,121,37,0.15)" }}>
        <p className="text-[10px] font-bold uppercase tracking-widest mb-3" style={{ color: "var(--vg-accent)" }}>Résumé du plan</p>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div><span style={{ color: "var(--vg-muted)" }}>Programme</span><br /><strong style={{ color: "var(--vg-fg)" }}>{state.partName}</strong></div>
          <div><span style={{ color: "var(--vg-muted)" }}>Risque</span><br /><strong style={{ color: state.result?.risk === "HIGH" ? "#DC2626" : state.result?.risk === "MEDIUM" ? "#D97706" : "#16A34A" }}>{state.result?.score}/100 — {state.result?.risk}</strong></div>
          <div><span style={{ color: "var(--vg-muted)" }}>Items sélectionnés</span><br /><strong>{state.checklist.filter(i => i.selected !== false).length}</strong></div>
          <div><span style={{ color: "var(--vg-muted)" }}>Assignés</span><br /><strong>{state.checklist.filter(i => i.owner).length}</strong></div>
        </div>
      </div>

      {/* Export buttons */}
      <div className="space-y-3">
        {exports.map(({ key, label, sub, Icon, ext }) => {
          const isDone = done.includes(key)
          const isLoading = loading === key
          return (
            <button key={key} onClick={() => handle(key)}
              disabled={isLoading}
              className="w-full flex items-center gap-4 p-4 rounded-2xl transition-all text-left"
              style={{
                background: isDone ? "var(--vg-risk-low-bg)" : "var(--vg-surface)",
                border: isDone ? "1.5px solid var(--vg-risk-low)" : "1.5px solid var(--vg-border)",
                boxShadow: "var(--vg-shadow-card)",
                cursor: isLoading ? "wait" : "pointer",
              }}>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style={{ background: "var(--vg-surface-alt)" }}>
                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" style={{ color: "var(--vg-accent)" }} /> : <Icon className="w-5 h-5" style={{ color: isDone ? "#16A34A" : "var(--vg-fg)" }} />}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-sm" style={{ color: "var(--vg-fg)" }}>{label} <span className="text-xs font-normal" style={{ color: "var(--vg-muted)" }}>{ext}</span></p>
                <p className="text-xs" style={{ color: "var(--vg-muted)" }}>{sub}</p>
              </div>
              <Download className="w-4 h-4 shrink-0" style={{ color: isDone ? "#16A34A" : "var(--vg-muted)" }} />
            </button>
          )
        })}
      </div>

      <button onClick={onPrev} className="w-full mt-5 flex items-center justify-center gap-2 py-3 rounded-2xl text-sm font-semibold" style={{ background: "var(--vg-surface-alt)", color: "var(--vg-fg)", border: "1px solid var(--vg-border)" }}>
        <ArrowLeft className="w-4 h-4" /> Retour à la revue
      </button>
    </div>
  )
}
