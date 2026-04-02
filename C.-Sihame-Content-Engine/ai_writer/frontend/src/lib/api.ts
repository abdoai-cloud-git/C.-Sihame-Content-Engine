const DEFAULT_DEV_API_URL = "http://localhost:8000";

function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (configured) {
    return stripTrailingSlash(configured);
  }

  // Fallback for local development
  if (process.env.NODE_ENV !== "production") {
    return DEFAULT_DEV_API_URL;
  }

  // On Vercel build-time, NEXT_PUBLIC_API_URL might be missing.
  // Instead of throwing and breaking the build, we return an empty string.
  // The actual fetch calls should handle this or wait for runtime.
  if (typeof window === "undefined") {
    console.warn("NEXT_PUBLIC_API_URL is missing during build-time. This is expected if it's only set in Runtimes.");
    return "";
  }

  // If we're in the browser and it's still missing, we handle it as an error.
  console.error("NEXT_PUBLIC_API_URL is not configured for production.");
  return "";
}
