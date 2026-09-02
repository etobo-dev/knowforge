export const AUTH_SESSION_STORAGE_KEY = "knowforge-auth-session";

export type CognitoTokenResponse = {
  access_token: string;
  refresh_token?: string;
  expires_in: number;
  token_type: string;
};

type StoredAuthSession = {
  accessToken: string;
  refreshToken: string | null;
  expiresAt: number;
};

function readStoredSession(): StoredAuthSession | null {
  if (typeof window === "undefined") return null;

  try {
    const raw = sessionStorage.getItem(AUTH_SESSION_STORAGE_KEY);
    if (!raw) return null;

    const parsed = JSON.parse(raw) as StoredAuthSession;
    if (
      typeof parsed.accessToken !== "string" ||
      typeof parsed.expiresAt !== "number"
    ) {
      return null;
    }

    return {
      accessToken: parsed.accessToken,
      refreshToken:
        typeof parsed.refreshToken === "string" ? parsed.refreshToken : null,
      expiresAt: parsed.expiresAt,
    };
  } catch {
    return null;
  }
}

function writeStoredSession(session: StoredAuthSession): void {
  sessionStorage.setItem(AUTH_SESSION_STORAGE_KEY, JSON.stringify(session));
}

export function saveAuthSession(tokens: CognitoTokenResponse): void {
  if (typeof window === "undefined") {
    throw new Error("saveAuthSession can only run in the browser");
  }

  writeStoredSession({
    accessToken: tokens.access_token,
    refreshToken: tokens.refresh_token ?? null,
    expiresAt: Date.now() + tokens.expires_in * 1000,
  });
}

export function getAuthSession(): StoredAuthSession | null {
  const session = readStoredSession();
  if (!session) return null;
  if (session.expiresAt <= Date.now()) {
    clearAuthSession();
    return null;
  }
  return session;
}

export function getAccessToken(): string | null {
  return getAuthSession()?.accessToken ?? null;
}

export function getRefreshToken(): string | null {
  return getAuthSession()?.refreshToken ?? null;
}

export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}

export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(AUTH_SESSION_STORAGE_KEY);
}
