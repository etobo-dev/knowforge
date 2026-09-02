import {
  buildCognitoAuthorizeUrl,
  buildCognitoLogoutUrl,
  getCognitoConfig,
  getLogoutRedirectUri,
  getOAuthRedirectUri,
} from "@/lib/auth/config";
import { clearAuthSession } from "@/lib/auth/session";

export function startGoogleLogin(): void {
  if (typeof window === "undefined") {
    throw new Error("startGoogleLogin can only run in the browser");
  }

  const config = getCognitoConfig();
  const redirectUri = getOAuthRedirectUri(window.location.origin);
  window.location.assign(
    buildCognitoAuthorizeUrl({
      config,
      redirectUri,
    }),
  );
}

export function startLogout(): void {
  if (typeof window === "undefined") {
    throw new Error("startLogout can only run in the browser");
  }

  const config = getCognitoConfig();
  const logoutUri = getLogoutRedirectUri(window.location.origin);
  clearAuthSession();
  window.location.assign(
    buildCognitoLogoutUrl({
      config,
      logoutUri,
    }),
  );
}
