"use client"
import { Moon, Sun, Plus } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

interface Props {
  hasResult: boolean
  onNew: () => void
}

export function TopBar({ hasResult, onNew }: Props) {
  const { theme, setTheme } = useTheme()
  const dark = theme === "dark"

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 h-14 flex items-center px-4 gap-4"
      style={{
        background: "linear-gradient(135deg, #16283F 0%, #1F3553 100%)",
        borderBottom: "2px solid #CD7925",
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 mr-auto">
        <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="18" stroke="#CD7925" strokeWidth="2.5" />
          <path d="M12 20 L20 10 L28 20 L20 30 Z" fill="#CD7925" opacity="0.85" />
          <circle cx="20" cy="20" r="4" fill="#EAF0F7" />
        </svg>
        <div>
          <span style={{ fontFamily: "var(--font-display, 'Barlow Condensed', sans-serif)", fontWeight: 700, fontSize: 15, color: "#EAF0F7", letterSpacing: 1 }}>
            VERSIGENT
          </span>
          <span style={{ fontSize: 10, color: "#9FB0C3", marginLeft: 8, letterSpacing: 2, textTransform: "uppercase" }}>
            Safe Launch
          </span>
        </div>
      </div>

      {hasResult && (
        <Button
          variant="outline"
          size="sm"
          onClick={onNew}
          className="h-8 gap-1 text-xs border-white/20 text-white/80 hover:bg-white/10 hover:text-white bg-transparent"
        >
          <Plus className="w-3.5 h-3.5" />
          Nouveau
        </Button>
      )}

      <button
        onClick={() => setTheme(dark ? "light" : "dark")}
        className="w-8 h-8 flex items-center justify-center rounded-md text-white/70 hover:text-white hover:bg-white/10 transition-colors"
        aria-label="Toggle dark mode"
      >
        {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>
    </header>
  )
}
