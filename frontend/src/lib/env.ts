const RAW = import.meta.env.VITE_AGUI_URL;

/**
 * Canonical AG-UI run endpoint URL (FR-007).
 * Rejects missing configuration at read time.
 */
export function getAgUiUrl(): string {
  if (typeof RAW !== "string" || RAW.trim().length === 0) {
    throw new Error(
      "VITE_AGUI_URL is required (e.g. http://localhost:7777/agui). Copy frontend/.env.example to frontend/.env.local.",
    );
  }
  return RAW.trim();
}
