export type Scene = 'Study' | 'Remote Work' | 'Date' | 'Meeting'

export interface ShopFeatures {
  noise: number // 1-5
  outlets: number // 1-5
  wifi: number // 1-5
  seating: number // 1-5
  lighting: number // 1-5
  privacy: number // 1-5
}

export interface ScoreBreakdown {
  feature: string
  weight: number
  normalizedValue: number
  contribution: number
}

export interface SuitabilityScore {
  score: number // 0-100
  breakdown: ScoreBreakdown[]
}

// Scene weights configuration
const SCENE_WEIGHTS: Record<Scene, Partial<Record<keyof ShopFeatures | 'rating', number>>> = {
  'Study': {
    noise: 0.30,
    outlets: 0.20,
    seating: 0.20,
    lighting: 0.15,
    wifi: 0.15,
  },
  'Remote Work': {
    wifi: 0.30,
    outlets: 0.25,
    seating: 0.20,
    noise: 0.15,
    lighting: 0.10,
  },
  'Date': {
    privacy: 0.30,
    lighting: 0.25,
    noise: 0.20,
    seating: 0.15,
    rating: 0.10,
  },
  'Meeting': {
    seating: 0.25,
    noise: 0.25,
    privacy: 0.20,
    wifi: 0.15,
    lighting: 0.15,
  },
}

/**
 * Normalize a value from 1-5 range to 0-1 range
 */
function normalize(value: number): number {
  return (value - 1) / 4
}

/**
 * Invert a normalized value (for noise where lower is better)
 */
function invert(normalized: number): number {
  return 1 - normalized
}

/**
 * Compute suitability score for a shop given a scene and features
 */
export function computeSuitability(
  scene: Scene,
  features: ShopFeatures,
  rating: number = 0
): SuitabilityScore {
  const weights = SCENE_WEIGHTS[scene]
  const breakdown: ScoreBreakdown[] = []
  let totalScore = 0

  // Process each feature
  for (const [feature, weight] of Object.entries(weights)) {
    if (weight === undefined || weight === 0) continue

    const featureKey = feature as keyof ShopFeatures | 'rating'
    let normalizedValue: number
    let contribution: number

    if (featureKey === 'noise') {
      // Invert noise (lower is better)
      normalizedValue = invert(normalize(features[featureKey]))
    } else if (featureKey === 'rating') {
      // Rating is 0-5, normalize to 0-1
      normalizedValue = rating / 5
    } else {
      // Normalize other features (higher is better)
      normalizedValue = normalize(features[featureKey])
    }

    contribution = normalizedValue * weight
    totalScore += contribution

    breakdown.push({
      feature: featureKey,
      weight,
      normalizedValue,
      contribution: contribution * 100, // Convert to percentage for display
    })
  }

  // Ensure score is between 0-100
  const score = Math.round(Math.min(100, Math.max(0, totalScore * 100)))

  return {
    score,
    breakdown: breakdown.sort((a, b) => b.contribution - a.contribution), // Sort by contribution descending
  }
}

