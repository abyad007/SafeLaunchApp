const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? "API error")
  }
  return res.json()
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(res.statusText)
  return res.json()
}

export const api = {
  programTypes: () => get<{ value: string; label: string }[]>("/api/program-types"),
  customers:    () => get<{ value: string; label: string; color: string; gates: string[] }[]>("/api/customers"),
  score:        (body: object) => post<import("./types").ScoreResult>("/api/score", body),
  plan:         (body: object) => post<import("./types").ChecklistItem[]>("/api/plan", body),
  exportPpt:    async (body: object) => {
    const res = await fetch(`${BASE}/api/export/ppt`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(await res.text())
    return res.blob()
  },
  exportExcel:  async (body: object) => {
    const res = await fetch(`${BASE}/api/export/excel`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(await res.text())
    return res.blob()
  },
}
