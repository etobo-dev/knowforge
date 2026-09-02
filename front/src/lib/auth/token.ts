import type { CognitoConfig } from "@/lib/auth/config";
import type { CognitoTokenResponse } from "@/lib/auth/session";

function isTokenResponse(value: unknown): value is CognitoTokenResponse {
  if (typeof value !== "object" || value === null) return false;
  const record = value as Record<string, unknown>;
  return (
    typeof record.access_token === "string" &&
    typeof record.expires_in === "number" &&
    typeof record.token_type === "string"
  );
}

export async function exchangeAuthorizationCode(params: {
  config: CognitoConfig;
  code: string;
  redirectUri: string;
}): Promise<CognitoTokenResponse> {
  const response = await fetch(
    `${params.config.hostedUiBaseUrl}/oauth2/token`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        client_id: params.config.clientId,
        code: params.code,
        redirect_uri: params.redirectUri,
      }),
    },
  );

  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok || !isTokenResponse(payload)) {
    throw new Error("Failed to exchange authorization code for tokens");
  }

  return payload;
}
