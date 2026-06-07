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
        <svg width="28" height="28" viewBox="0 0 191 190" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M57.7058 70.6293C69.8627 83.0319 79.3746 97.9261 88.5794 112.333C97.0864 125.647 105.154 138.266 114.819 148.267C113.109 143.019 111.874 137.424 111.107 131.375C109.173 116.238 110.388 100.251 111.567 84.7718C113.856 54.712 115.852 24.2415 94.616 -0.00683594C60.6927 0.104523 30.9636 17.9567 14.2637 44.7315C30.6007 49.0049 44.8302 57.482 57.7058 70.6223V70.6293Z" fill="#CD7924"/>
          <path d="M95.0493 161.101C84.6581 149.902 76.3326 136.184 68.2722 122.912C52.64 97.1462 36.5193 71.2275 5.17119 63.7734C1.82143 73.4477 0 83.8389 0 94.6546C0 146.93 42.4931 189.309 94.9098 189.309C106.62 189.309 117.828 187.187 128.184 183.324C115.72 179.057 105.078 171.896 95.0563 161.101H95.0493Z" fill="#CD7924"/>
          <path d="M123.146 4.19727C128.324 13.7045 131.785 24.2697 133.628 36.1085C136.293 53.2507 135.358 70.8802 134.451 87.9389C133.558 104.879 132.706 120.873 135.365 135.447C137.815 148.873 143.077 159.556 151.402 167.992C151.549 168.013 151.688 168.041 151.835 168.054V168.416C152.24 168.82 152.651 169.217 153.07 169.607C175.541 152.297 190.015 125.161 190.015 94.6552C190.015 52.1093 161.87 16.1266 123.139 4.19727H123.146Z" fill="#CD7924"/>
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
