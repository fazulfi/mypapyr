import { ImageResponse } from "next/og";

export const alt = "Papyr — Free PDF tools";

export const size = {
  width: 1200,
  height: 630,
};

export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    <div
      style={{
        background: "linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%)",
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px",
      }}
    >
      {/* Logo */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "20px",
          marginBottom: "40px",
        }}
      >
        <div
          style={{
            width: "80px",
            height: "80px",
            borderRadius: "16px",
            background: "rgba(255, 255, 255, 0.15)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
        </div>
        <span
          style={{
            fontSize: "64px",
            fontWeight: 700,
            color: "white",
            letterSpacing: "-1px",
          }}
        >
          Papyr
        </span>
      </div>

      {/* Tagline */}
      <div
        style={{
          fontSize: "36px",
          color: "rgba(255, 255, 255, 0.9)",
          textAlign: "center",
          maxWidth: "800px",
          lineHeight: 1.4,
        }}
      >
        Free PDF tools for everyone
      </div>

      {/* Features */}
      <div
        style={{
          display: "flex",
          gap: "32px",
          marginTop: "48px",
        }}
      >
        {["Compress", "Merge", "Split", "Convert"].map((tool) => (
          <div
            key={tool}
            style={{
              background: "rgba(255, 255, 255, 0.12)",
              borderRadius: "12px",
              padding: "12px 24px",
              fontSize: "20px",
              color: "rgba(255, 255, 255, 0.85)",
            }}
          >
            {tool}
          </div>
        ))}
      </div>

      {/* Bottom tagline */}
      <div
        style={{
          position: "absolute",
          bottom: "40px",
          fontSize: "18px",
          color: "rgba(255, 255, 255, 0.5)",
        }}
      >
        budgezen.com · Free · No account needed · Auto-delete 1 hour
      </div>
    </div>,
    {
      ...size,
    },
  );
}
