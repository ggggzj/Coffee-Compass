"use client";

// MapAdapter boundary: this is the ONLY module that imports the map provider.
// page.tsx talks to it with provider-agnostic props (recommendations + selection),
// so swapping Mapbox for another provider means rewriting only this file.

import { useMemo } from "react";
import Link from "next/link";
import Map, { Marker, Popup } from "react-map-gl/mapbox";
import "mapbox-gl/dist/mapbox-gl.css";
import type { Recommendation } from "@/lib/api";
import styles from "./MapPanel.module.css";

// USC main campus — the default center / "near me" reference (W3.6).
const USC = { longitude: -118.2851, latitude: 34.0224, zoom: 13 };

const TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN ?? "";
const TOKEN_READY = TOKEN.startsWith("pk.") && !TOKEN.includes("your_public");

export default function MapPanel({
  recommendations,
  selectedCafeId,
  onSelectCafe,
}: {
  recommendations: Recommendation[];
  selectedCafeId: number | null;
  onSelectCafe: (id: number | null) => void;
}) {
  const selected = useMemo(
    () => recommendations.find((r) => r.id === selectedCafeId) ?? null,
    [recommendations, selectedCafeId]
  );

  if (!TOKEN_READY) {
    return (
      <div className={styles.hint}>
        <p>
          Add your Mapbox <strong>public</strong> token to <code>frontend/.env.local</code> as
          <br />
          <code>NEXT_PUBLIC_MAPBOX_TOKEN=pk.…</code>
          <br />
          then restart <code>npm run dev</code>.
        </p>
      </div>
    );
  }

  return (
    <Map
      mapboxAccessToken={TOKEN}
      initialViewState={USC}
      mapStyle="mapbox://styles/mapbox/streets-v12"
      style={{ width: "100%", height: "100%" }}
    >
      {recommendations.map((r) => {
        const active = r.id === selectedCafeId;
        return (
          <Marker
            key={r.id}
            longitude={r.lng}
            latitude={r.lat}
            anchor="bottom"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              onSelectCafe(active ? null : r.id);
            }}
          >
            <button
              type="button"
              className={`${styles.pin} ${active ? styles.pinActive : ""}`}
              onMouseEnter={() => onSelectCafe(r.id)}
              aria-label={r.name}
            >
              ☕
            </button>
          </Marker>
        );
      })}

      {selected && (
        <Popup
          longitude={selected.lng}
          latitude={selected.lat}
          anchor="top"
          closeButton={false}
          offset={16}
        >
          <div className={styles.popup}>
            <strong>{selected.name}</strong>
            {selected.price_level != null && <span> · {"$".repeat(selected.price_level)}</span>}
            {selected.open_now && <span className={styles.open}> · open</span>}
            <Link href={`/cafe/${selected.id}`} className={styles.detailsLink}>
              View details →
            </Link>
          </div>
        </Popup>
      )}
    </Map>
  );
}
