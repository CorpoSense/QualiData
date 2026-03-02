// API utility - handles API URL for both dev and production
export function getApiUrl() {
  // In production (deployed), use relative URL (same domain)
  if (import.meta.env.PROD || (typeof window !== 'undefined' && window.location.hostname !== 'localhost')) {
    return ''
  }
  // In development, use configured URL or localhost
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}
