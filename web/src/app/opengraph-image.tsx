import { ImageResponse } from "next/og";

export const alt = "Lysis: find beginner-friendly GitHub issues";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: 80,
          background: "#09090b",
          color: "#fafafa",
        }}
      >
        <div style={{ fontSize: 40, color: "#34d399" }}>lysis</div>
        <div style={{ fontSize: 68, fontWeight: 700, marginTop: 24, lineHeight: 1.1 }}>
          Find the GitHub issues a beginner can actually finish.
        </div>
        <div style={{ fontSize: 30, color: "#a1a1aa", marginTop: 32 }}>trylysis.me</div>
      </div>
    ),
    size,
  );
}


