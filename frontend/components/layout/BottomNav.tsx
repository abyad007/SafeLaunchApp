"use client"
import { Settings, BarChart2, ClipboardCheck, Upload } from "lucide-react"

const TABS = [
  { step: 1, label: "Config",  Icon: Settings },
  { step: 2, label: "Tableau", Icon: BarChart2 },
  { step: 3, label: "Revue",   Icon: ClipboardCheck },
  { step: 4, label: "Export",  Icon: Upload },
] as const

interface Props {
  step: 1 | 2 | 3 | 4
  hasResult: boolean
  onStep: (s: 1 | 2 | 3 | 4) => void
}

export function BottomNav({ step, hasResult, onStep }: Props) {
  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 flex items-stretch"
      style={{
        background: "var(--vg-surface)",
        borderTop: "1px solid var(--vg-border)",
        boxShadow: "0 -2px 14px rgba(22,40,63,0.07)",
        paddingBottom: "env(safe-area-inset-bottom)",
      }}
    >
      {TABS.map(({ step: s, label, Icon }) => {
        const active = step === s
        const disabled = s > 1 && !hasResult
        return (
          <button
            key={s}
            disabled={disabled}
            onClick={() => onStep(s as 1 | 2 | 3 | 4)}
            className="flex-1 flex flex-col items-center justify-center gap-1 py-2 transition-colors disabled:opacity-30"
            style={{
              color: active ? "var(--vg-accent)" : "var(--vg-muted)",
              fontWeight: active ? 700 : 500,
              fontSize: 10,
              letterSpacing: "0.5px",
              background: "transparent",
              border: "none",
              cursor: disabled ? "not-allowed" : "pointer",
            }}
          >
            <Icon
              className="w-5 h-5"
              strokeWidth={active ? 2.2 : 1.8}
            />
            <span style={{ textTransform: "uppercase" }}>{label}</span>
          </button>
        )
      })}
    </nav>
  )
}
