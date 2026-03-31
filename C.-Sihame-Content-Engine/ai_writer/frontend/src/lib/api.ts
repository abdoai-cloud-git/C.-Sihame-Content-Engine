const DEFAULT_DEV_API_URL = "http://localhost:8000";

function stripTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (configured) {
    return stripTrailingSlash(configured);
  }

  if (process.env.NODE_ENV !== "production") {
    return DEFAULT_DEV_API_URL;
  }

  throw new Error("NEXT_PUBLIC_API_URL is not configured.");
}
