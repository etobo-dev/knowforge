"use client";

import { LogIn, LogOut } from "lucide-react";
import { useSyncExternalStore } from "react";

import {
  isAuthenticated,
  startGoogleLogin,
  startLogout,
  subscribeAuthChanged,
} from "@/lib/auth";

export function AuthControls() {
  const signedIn = useSyncExternalStore(
    subscribeAuthChanged,
    isAuthenticated,
    () => false,
  );

  if (signedIn) {
    return (
      <button
        type="button"
        onClick={() => startLogout()}
        className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-sidebar-text transition-colors hover:bg-sidebar-active/50"
      >
        <LogOut size={14} className="opacity-60" aria-hidden />
        Sign out
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={() => startGoogleLogin()}
      className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-sidebar-text transition-colors hover:bg-sidebar-active/50"
    >
      <LogIn size={14} className="opacity-60" aria-hidden />
      Sign in with Google
    </button>
  );
}
