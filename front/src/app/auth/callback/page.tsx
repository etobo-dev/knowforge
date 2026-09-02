"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import {
  exchangeAuthorizationCode,
  getCognitoConfig,
  getOAuthRedirectUri,
  saveAuthSession,
} from "@/lib/auth";

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [exchangeError, setExchangeError] = useState<string | null>(null);

  const code = searchParams.get("code");
  const oauthError = searchParams.get("error");
  const oauthErrorDescription = searchParams.get("error_description");
  const queryError =
    oauthErrorDescription ??
    oauthError ??
    (code ? null : "Missing authorization code");
  const error = exchangeError ?? queryError;

  useEffect(() => {
    if (queryError || !code) return;

    let cancelled = false;

    async function completeLogin(authorizationCode: string) {
      try {
        const config = getCognitoConfig();
        const redirectUri = getOAuthRedirectUri(window.location.origin);
        const tokens = await exchangeAuthorizationCode({
          config,
          code: authorizationCode,
          redirectUri,
        });
        if (cancelled) return;
        saveAuthSession(tokens);
        router.replace("/");
      } catch (err) {
        if (cancelled) return;
        setExchangeError(
          err instanceof Error ? err.message : "Sign-in failed. Try again.",
        );
      }
    }

    void completeLogin(code);

    return () => {
      cancelled = true;
    };
  }, [code, queryError, router]);

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 px-8 text-center">
        <h1 className="text-xl font-semibold text-text-primary">
          Sign-in failed
        </h1>
        <p className="max-w-md text-sm text-text-secondary">{error}</p>
        <button
          type="button"
          onClick={() => router.replace("/")}
          className="mt-2 rounded-lg bg-sidebar-active px-4 py-2 text-sm text-white"
        >
          Back to home
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-full items-center justify-center px-8">
      <p className="text-sm text-text-secondary">Completing sign-in…</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center px-8">
          <p className="text-sm text-text-secondary">Completing sign-in…</p>
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  );
}
