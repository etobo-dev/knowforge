export type CognitoConfig = {
  clientId: string;
  hostedUiBaseUrl: string;
};

const OAUTH_SCOPES = "openid email profile";

export function getCognitoConfig(): CognitoConfig {
  const clientId = process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID;
  const hostedUiBaseUrl = process.env.NEXT_PUBLIC_COGNITO_HOSTED_UI_BASE_URL;

  if (!clientId || !hostedUiBaseUrl) {
    throw new Error(
      "Missing NEXT_PUBLIC_COGNITO_CLIENT_ID or NEXT_PUBLIC_COGNITO_HOSTED_UI_BASE_URL",
    );
  }

  return {
    clientId,
    hostedUiBaseUrl: hostedUiBaseUrl.replace(/\/$/, ""),
  };
}

export function getOAuthRedirectUri(origin: string): string {
  return `${origin.replace(/\/$/, "")}/auth/callback`;
}

export function getLogoutRedirectUri(origin: string): string {
  return origin.replace(/\/$/, "");
}

export function buildCognitoAuthorizeUrl(params: {
  config: CognitoConfig;
  redirectUri: string;
  state?: string;
}): string {
  const url = new URL(`${params.config.hostedUiBaseUrl}/oauth2/authorize`);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", params.config.clientId);
  url.searchParams.set("redirect_uri", params.redirectUri);
  url.searchParams.set("scope", OAUTH_SCOPES);
  url.searchParams.set("identity_provider", "Google");
  if (params.state) {
    url.searchParams.set("state", params.state);
  }
  return url.toString();
}

export function buildCognitoLogoutUrl(params: {
  config: CognitoConfig;
  logoutUri: string;
}): string {
  const url = new URL(`${params.config.hostedUiBaseUrl}/logout`);
  url.searchParams.set("client_id", params.config.clientId);
  url.searchParams.set("logout_uri", params.logoutUri);
  return url.toString();
}
