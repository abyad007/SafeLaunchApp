export type Risk = "LOW" | "MEDIUM" | "HIGH"
export type ProgType = "new" | "new_plant" | "transfer" | "my_change" | "restart" | "absence" | "capacity"

export interface ScoreFactor {
  name: string
  value: number
  max: number
  percent: number
}

export interface ScoreResult {
  score: number
  risk: Risk
  duration: number
  fpy: string
  inspection: string
  ppap: string
  recommendation: string
  factors: ScoreFactor[]
  pra_forecast: string
  conformance: number
}

export interface ChecklistItem {
  step: string
  text: string
  phase: string
  critical: boolean
  warn: boolean
  done: boolean
  owner: string
  due: string
  selected?: boolean
}

export interface ProgramType {
  value: ProgType
  label: string
}

export interface Customer {
  value: string
  label: string
  color: string
  gates: string[]
}

export interface WizardState {
  step: 1 | 2 | 3 | 4
  progType: ProgType | ""
  partName: string
  customer: string
  inputs: Record<string, unknown>
  result: ScoreResult | null
  checklist: ChecklistItem[]
  meta: Record<string, string>
}
