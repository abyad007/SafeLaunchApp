"use client"
import { useState, useCallback } from "react"
import { WizardState } from "@/lib/types"
import { api } from "@/lib/api"
import { TopBar } from "@/components/layout/TopBar"
import { BottomNav } from "@/components/layout/BottomNav"
import { Stepper } from "@/components/wizard/Stepper"
import { Step1Config } from "@/components/steps/Step1Config"
import { Step2Dashboard } from "@/components/steps/Step2Dashboard"
import { Step3Review } from "@/components/steps/Step3Review"
import { Step4Export } from "@/components/steps/Step4Export"

const INIT: WizardState = {
  step: 1,
  progType: "",
  partName: "",
  customer: "",
  inputs: { pfmea: 5, headcount: 30, volume: 1000, critical: "yes", prod_system: "batch", np_experience: "known" },
  result: null,
  checklist: [],
  meta: {},
}

export default function Home() {
  const [state, setState] = useState<WizardState>(INIT)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const patch = useCallback((partial: Partial<WizardState>) => {
    setState(s => ({ ...s, ...partial }))
  }, [])

  const goTo = (step: 1 | 2 | 3 | 4) => patch({ step })

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    try {
      const inputs = {
        ...state.inputs,
        customer: state.customer,
      }
      const [result, checklist] = await Promise.all([
        api.score({ prog_type: state.progType, inputs }),
        api.plan({
          prog_type: state.progType,
          context: { ...inputs, part_name: state.partName, primary_date: state.meta.primary_date },
        }),
      ])
      patch({ result, checklist: checklist.map(i => ({ ...i, selected: true })), step: 2 })
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen" style={{ background: "var(--vg-bg)" }}>
      <TopBar hasResult={!!state.result} onNew={() => setState(INIT)} />

      {/* Main content */}
      <main className="pt-14 pb-20 px-4 max-w-4xl mx-auto">
        {/* Stepper */}
        <div className="py-5">
          <Stepper step={state.step} />
        </div>

        {/* Error */}
        {error && (
          <div className="mb-4 px-4 py-3 rounded-xl text-sm" style={{ background: "var(--vg-risk-high-bg)", color: "var(--vg-risk-high)", border: "1px solid var(--vg-risk-high)" }}>
            Erreur : {error}
          </div>
        )}

        {/* Steps */}
        {state.step === 1 && (
          <Step1Config state={state} onChange={patch} onSubmit={handleGenerate} loading={loading} />
        )}
        {state.step === 2 && state.result && (
          <Step2Dashboard state={state} onPrev={() => goTo(1)} onNext={() => goTo(3)} />
        )}
        {state.step === 3 && (
          <Step3Review state={state} onChange={patch} onPrev={() => goTo(2)} onNext={() => goTo(4)} />
        )}
        {state.step === 4 && (
          <Step4Export state={state} onPrev={() => goTo(3)} />
        )}
      </main>

      <BottomNav step={state.step} hasResult={!!state.result} onStep={goTo} />
    </div>
  )
}
