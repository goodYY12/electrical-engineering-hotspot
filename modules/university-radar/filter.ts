import type { UniversityRadarEntry } from "./server.ts";

export interface UniversityRadarFilters {
  university?: string | null;
  region?: string | null;
  direction?: string | null;
}

export function filterUniversityEntries(entries: UniversityRadarEntry[], filters: UniversityRadarFilters) {
  return entries.filter((entry) => (!filters.university || entry.university === filters.university)
    && (!filters.region || entry.region === filters.region)
    && (!filters.direction || entry.researchDirections.some((direction) => direction.includes(filters.direction!))));
}
