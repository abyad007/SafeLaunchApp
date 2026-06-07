"use client"
import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import { WizardState, ProgramType, Customer } from "@/lib/types"
import { ArrowRight, Loader2, Info } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface Props {
  state: WizardState
  onChange: (partial: Partial<WizardState>) => void
  onSubmit: () => Promise<void>
  loading: boolean
}

const EXPERIENCE = [
  { value: "known",  label: "Customer known — similar product" },
  { value: "medium", label: "Customer known — different product" },
  { value: "new",    label: "New customer / new product" },
]

const FIELD = "border rounded-xl px-4 py-3 w-full text-sm transition-all outline-none"
const FIELD_STYLE = {
  background: "var(--vg-surface-alt)",
  border: "1.5px solid var(--vg-border)",
  color: "var(--vg-fg)",
}
const FOCUS_RING = {
  "--focus-border": "var(--vg-accent)",
} as React.CSSProperties

function Label({ children, tip }: { children: React.ReactNode; tip?: string }) {
  return (
    <label className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--vg-muted)" }}>
      {children}
      {tip && <span title={tip}><Info className="w-3 h-3 opacity-60" /></span>}
    </label>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl p-5 mb-4" style={{ background: "var(--vg-surface)", border: "1px solid var(--vg-border)", boxShadow: "var(--vg-shadow-card)" }}>
      <p className="text-[10px] font-bold uppercase tracking-[2px] mb-4" style={{ color: "var(--vg-accent)" }}>{title}</p>
      {children}
    </div>
  )
}

export function Step1Config({ state, onChange, onSubmit, loading }: Props) {
  const [progTypes, setProgTypes] = useState<ProgramType[]>([])
  const [customers, setCustomers] = useState<Customer[]>([])

  useEffect(() => {
    api.programTypes().then(d => setProgTypes(d as ProgramType[]))
    api.customers().then(setCustomers)
  }, [])

  const inp = state.inputs as Record<string, string | number>
  const set = (k: string, v: unknown) => onChange({ inputs: { ...state.inputs, [k]: v } })

  const ready = !!state.progType && !!state.partName && !!state.meta.primary_date

  return (
    <div className="max-w-2xl mx-auto pb-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-1" style={{ fontFamily: "var(--font-display, sans-serif)", color: "var(--vg-fg)" }}>
          Étape 1 · Configurer le programme
        </h1>
        <p className="text-sm" style={{ color: "var(--vg-muted)" }}>
          Renseignez le contexte — le formulaire s'adapte au type de programme.
        </p>
      </div>

      {/* Program identity */}
      <Section title="Programme">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div>
            <Label>Type de programme</Label>
            <select
              className={FIELD}
              style={FIELD_STYLE}
              value={state.progType}
              onChange={e => onChange({ progType: e.target.value as WizardState["progType"] })}
            >
              <option value="">— Sélectionner —</option>
              {progTypes.map(pt => <option key={pt.value} value={pt.value}>{pt.label}</option>)}
            </select>
          </div>
          <div>
            <Label>Client / OEM</Label>
            <select
              className={FIELD}
              style={FIELD_STYLE}
              value={state.customer}
              onChange={e => onChange({ customer: e.target.value, inputs: { ...state.inputs, customer: e.target.value } })}
            >
              <option value="">— Sélectionner —</option>
              {customers.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
        </div>
        <div>
          <Label>Nom de la pièce / projet</Label>
          <input
            type="text"
            className={FIELD}
            style={FIELD_STYLE}
            placeholder="ex. Bracket Assembly X200"
            value={state.partName}
            onChange={e => onChange({ partName: e.target.value })}
          />
        </div>
      </Section>

      {/* Key dates */}
      {state.progType && (
        <Section title="Dates clés">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <Label>SOP — Start of Production *</Label>
              <input type="date" className={FIELD} style={FIELD_STYLE}
                value={state.meta.primary_date ?? ""}
                onChange={e => onChange({ meta: { ...state.meta, primary_date: e.target.value } })} />
            </div>
            <div>
              <Label>VFF — Vehicle Functional Freeze</Label>
              <input type="date" className={FIELD} style={FIELD_STYLE}
                value={state.meta.vff_date ?? ""}
                onChange={e => onChange({ meta: { ...state.meta, vff_date: e.target.value } })} />
            </div>
            <div>
              <Label>Pre-Serial / Pilot Run</Label>
              <input type="date" className={FIELD} style={FIELD_STYLE}
                value={state.meta.pilot_date ?? ""}
                onChange={e => onChange({ meta: { ...state.meta, pilot_date: e.target.value } })} />
            </div>
          </div>
        </Section>
      )}

      {/* Team & Volume */}
      {state.progType && (
        <Section title="Équipe & Volume">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <Label tip="Nombre d'opérateurs en ligne au SOP">Opérateurs estimés en ligne</Label>
              <input type="number" min={1} max={500} className={FIELD} style={FIELD_STYLE}
                value={inp.headcount as number ?? 30}
                onChange={e => set("headcount", +e.target.value)} />
            </div>
            <div>
              <Label>Expérience équipe / client</Label>
              <select className={FIELD} style={FIELD_STYLE}
                value={inp.np_experience as string ?? "known"}
                onChange={e => set("np_experience", e.target.value)}>
                {EXPERIENCE.map(x => <option key={x.value} value={x.value}>{x.label}</option>)}
              </select>
            </div>
            <div>
              <Label>Volume journalier au SOP (pcs/jour)</Label>
              <input type="number" min={1} className={FIELD} style={FIELD_STYLE}
                value={inp.volume as number ?? 1000}
                onChange={e => set("volume", +e.target.value)} />
            </div>
            <div>
              <Label>Système de production</Label>
              <div className="flex gap-3 mt-1">
                {[["batch", "Batch Production"], ["ksk", "KSK System"]].map(([v, l]) => (
                  <label key={v} className="flex items-center gap-2 cursor-pointer text-sm" style={{ color: "var(--vg-fg)" }}>
                    <input type="radio" name="prod_system" value={v}
                      checked={(inp.prod_system ?? "batch") === v}
                      onChange={() => set("prod_system", v)}
                      className="accent-[var(--vg-accent)]" />
                    {l}
                  </label>
                ))}
              </div>
            </div>
          </div>
        </Section>
      )}

      {/* Risk factors */}
      {state.progType && (
        <Section title="Facteurs de risque">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <Label tip="Indice de sévérité max dans l'AMDEC processus">PFMEA Highest Severity (1–10)</Label>
              <input type="range" min={1} max={10} className="w-full accent-[#CD7925]"
                value={inp.pfmea as number ?? 5}
                onChange={e => set("pfmea", +e.target.value)} />
              <div className="flex justify-between text-xs mt-1" style={{ color: "var(--vg-muted)" }}>
                <span>1 — Faible</span>
                <span className="font-bold" style={{ color: "var(--vg-accent)" }}>{inp.pfmea ?? 5}</span>
                <span>10 — Critique</span>
              </div>
            </div>
            <div>
              <Label>Caractéristiques spéciales (SC)</Label>
              <div className="flex gap-3 mt-1">
                {[["yes", "Appliquées — SC identifiées"], ["no", "Non appliquées"]].map(([v, l]) => (
                  <label key={v} className="flex items-center gap-2 cursor-pointer text-sm" style={{ color: "var(--vg-fg)" }}>
                    <input type="radio" name="critical" value={v}
                      checked={(inp.critical ?? "yes") === v}
                      onChange={() => set("critical", v)}
                      className="accent-[var(--vg-accent)]" />
                    {l}
                  </label>
                ))}
              </div>
            </div>
          </div>
        </Section>
      )}

      {/* Submit */}
      {state.progType && (
        <button
          disabled={!ready || loading}
          onClick={onSubmit}
          className="w-full flex items-center justify-center gap-2 py-4 rounded-2xl font-bold text-base transition-all disabled:opacity-50"
          style={{
            background: ready ? "var(--vg-accent)" : "var(--vg-border)",
            color: ready ? "white" : "var(--vg-muted)",
            cursor: ready && !loading ? "pointer" : "not-allowed",
            boxShadow: ready ? "0 4px 16px rgba(205,121,37,0.3)" : "none",
          }}
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ArrowRight className="w-5 h-5" />}
          Générer le plan de lancement
        </button>
      )}
    </div>
  )
}
