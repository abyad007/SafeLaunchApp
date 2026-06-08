import { ImageResponse } from "next/og"

export const runtime = "edge"
export const alt = "Versigent Safe Launch Generator"
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: "linear-gradient(135deg, #16283F 0%, #1F3553 100%)",
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          fontFamily: "sans-serif",
        }}
      >
        {/* Copper bottom border */}
        <div style={{
          position: "absolute",
          bottom: 0, left: 0, right: 0,
          height: 8,
          background: "#CD7925",
        }} />

        {/* Top label */}
        <div style={{
          position: "absolute",
          top: 48,
          left: 72,
          color: "#CD7925",
          fontSize: 18,
          fontWeight: 700,
          letterSpacing: 4,
          textTransform: "uppercase",
        }}>
          Versigent
        </div>

        {/* Main content */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
          {/* Big title */}
          <div style={{
            fontSize: 72,
            fontWeight: 800,
            color: "#EAF0F7",
            letterSpacing: -1,
            textAlign: "center",
            lineHeight: 1.1,
          }}>
            Safe Launch
          </div>
          <div style={{
            fontSize: 72,
            fontWeight: 800,
            color: "#CD7925",
            letterSpacing: -1,
          }}>
            Generator
          </div>

          {/* Subtitle */}
          <div style={{
            fontSize: 24,
            color: "#9FB0C3",
            textAlign: "center",
            maxWidth: 800,
            lineHeight: 1.5,
            marginTop: 8,
          }}>
            Évaluation des risques · Plan qualité · Reporting PPAP
          </div>
        </div>

        {/* Bottom badges */}
        <div style={{
          position: "absolute",
          bottom: 48,
          display: "flex",
          gap: 16,
        }}>
          {["IATF 16949", "VDA 6.3", "PPAP Level 3", "APQP"].map((label) => (
            <div key={label} style={{
              background: "rgba(205,121,37,0.15)",
              border: "1px solid rgba(205,121,37,0.4)",
              borderRadius: 6,
              padding: "6px 14px",
              color: "#CD7925",
              fontSize: 14,
              fontWeight: 600,
              letterSpacing: 1,
            }}>
              {label}
            </div>
          ))}
        </div>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
