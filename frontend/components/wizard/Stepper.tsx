"use client"
import { Check } from "lucide-react"

const STEPS = ["Configurer", "Tableau de bord", "Revue", "Export"]

interface Props { step: number }

export function Stepper({ step }: Props) {
  return (
    <div className="flex items-center w-full">
      {STEPS.map((label, i) => {
        const n = i + 1
        const done = step > n
        const active = step === n
        return (
          <div key={n} className="flex items-center flex-1 last:flex-none">
            <div className="flex flex-col items-center gap-1 shrink-0">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all"
                style={{
                  background: done ? "var(--vg-accent)" : active ? "var(--vg-fg)" : "transparent",
                  border: `2px solid ${done || active ? "transparent" : "var(--vg-border)"}`,
                  color: done || active ? "white" : "var(--vg-muted)",
                }}
              >
                {done ? <Check className="w-4 h-4" /> : n}
              </div>
              <span
                className="text-[10px] font-semibold uppercase tracking-wide whitespace-nowrap hidden sm:block"
                style={{ color: active ? "var(--vg-fg)" : "var(--vg-muted)" }}
              >
                {label}
              </span>
            </div>
            {n < STEPS.length && (
              <div
                className="flex-1 h-px mx-2"
                style={{ background: step > n ? "var(--vg-accent)" : "var(--vg-border)" }}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
