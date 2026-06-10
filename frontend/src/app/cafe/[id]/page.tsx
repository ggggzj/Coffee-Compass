"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { fetchCafe, type CafeDetail } from "@/lib/api";
import styles from "./page.module.css";

function priceLabel(level: number | null) {
  return level != null ? "$".repeat(level) : "—";
}

export default function CafeDetailPage() {
  const params = useParams<{ id: string }>();
  const [cafe, setCafe] = useState<CafeDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const detail = await fetchCafe(params.id);
        if (active) setCafe(detail);
      } catch (e) {
        if (active) setError(String(e));
      }
    })();
    return () => {
      active = false;
    };
  }, [params.id]);

  return (
    <main className={styles.page}>
      <Link href="/" className={styles.back}>
        ← Back to search
      </Link>

      {error && <p className={styles.error}>Couldn&rsquo;t load this cafe ({error}).</p>}
      {!cafe && !error && <p className={styles.loading}>Loading…</p>}

      {cafe && (
        <article className={styles.card}>
          <h1>{cafe.name}</h1>
          <p className={styles.address}>{cafe.address}</p>

          <div className={styles.meta}>
            {cafe.rating != null && <span>★ {cafe.rating.toFixed(1)}</span>}
            <span>{priceLabel(cafe.price_level)}</span>
            {cafe.noise_level && <span>{cafe.noise_level}</span>}
            {cafe.has_outlet && <span>outlets</span>}
            {cafe.has_wifi && <span>wifi</span>}
            {cafe.good_for_studying && <span>good for studying</span>}
          </div>

          {cafe.ambience_text && <p className={styles.ambience}>{cafe.ambience_text}</p>}
          {cafe.editorial_summary && <p className={styles.editorial}>{cafe.editorial_summary}</p>}

          {cafe.categories && cafe.categories.length > 0 && (
            <div className={styles.tags}>
              {cafe.categories.map((c) => (
                <span key={c} className={styles.tag}>
                  {c}
                </span>
              ))}
            </div>
          )}

          <p className={styles.coords}>
            {cafe.lat.toFixed(5)}, {cafe.lng.toFixed(5)}
          </p>
        </article>
      )}
    </main>
  );
}
