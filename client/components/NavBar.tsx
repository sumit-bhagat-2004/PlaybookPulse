"use client";

import { useState, useEffect } from "react";
import { SignInButton, UserButton, useUser } from "@clerk/nextjs";
import { Menu, X, ShieldCheck, Bell, GitBranch } from "lucide-react";
import Link from "next/link";

const NAV_LINKS = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Incidents", href: "/incidents" },
  { label: "Playbooks", href: "/playbooks" },
  { label: "Evidence", href: "/evidence" },
];

export default function Navbar() {
  const { isSignedIn } = useUser();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <nav className="fixed top-0 inset-x-0 z-50 bg-black border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20 py-2">
            {/* ── LOGO ── */}
            <Link
              href="/"
              className="flex items-center gap-3 group select-none"
            >
              <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-to-br from-blue-600 to-blue-700 border border-blue-400/50 shadow-[0_0_16px_rgba(59,130,246,0.5)] group-hover:from-blue-500 group-hover:to-blue-600 group-hover:border-blue-300 group-hover:shadow-[0_0_24px_rgba(59,130,246,0.7)] transition-all duration-300">
                <ShieldCheck className="w-5 h-5 text-white" strokeWidth={2.5} />
              </div>
              <span className="text-base font-bold tracking-tight text-white font-mono">
                Playbook
                <span className="text-blue-400">Pulse</span>
              </span>
            </Link>

            {/* ── DESKTOP NAV ── */}
            {isSignedIn && (
              <div className="hidden md:flex items-center gap-8 absolute left-1/2 -translate-x-1/2">
                {NAV_LINKS.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="text-sm font-medium text-neutral-400 hover:text-white hover:drop-shadow-[0_0_12px_rgba(255,255,255,0.3)] transition-all duration-200"
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            )}

            {/* ── RIGHT SIDE ── */}
            <div className="flex items-center gap-4">
              {isSignedIn ? (
                <>
                  <div className="hidden sm:flex items-center gap-4 pr-5 border-r border-white/10">
                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-neutral-900/50 border border-white/5 text-xs text-neutral-400 font-mono shadow-inner">
                      <GitBranch className="w-3.5 h-3.5 text-blue-500" />
                      <span>main</span>
                    </div>

                    <button
                      className="relative text-neutral-400 hover:text-white transition-colors duration-200"
                      aria-label="Notifications"
                    >
                      <Bell className="w-4 h-4" />
                      <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-blue-500 ring-2 ring-black" />
                    </button>
                  </div>

                  {/* Built-in Clerk User Profile */}
                  <div className="pl-1">
                    <UserButton
                      appearance={{
                        elements: {
                          userButtonAvatarBox:
                            "w-8 h-8 ring-1 ring-white/10 hover:ring-white/30 transition-all shadow-lg",
                        },
                      }}
                    />
                  </div>
                </>
              ) : (
                <div className="hidden sm:block">
                  <SignInButton mode="modal" forceRedirectUrl="/dashboard">
                    <button className="px-6 py-2.5 rounded-lg text-sm font-semibold bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-600/20 transition-all duration-200 hover:shadow-blue-600/40">
                      Sign In
                    </button>
                  </SignInButton>
                </div>
              )}

              {/* ── MOBILE TOGGLE ── */}
              {(!isSignedIn || isSignedIn) && (
                <button
                  className="md:hidden p-1 text-neutral-400 hover:text-white transition-colors"
                  onClick={() => setMobileOpen((v) => !v)}
                  aria-label="Toggle menu"
                >
                  {mobileOpen ? (
                    <X className="w-5 h-5" />
                  ) : (
                    <Menu className="w-5 h-5" />
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* ── MOBILE DRAWER ── */}
        {mobileOpen && (
          <div className="md:hidden absolute top-16 left-0 w-full bg-black/95 backdrop-blur-2xl border-b border-white/5 shadow-2xl">
            <div className="px-4 py-4 flex flex-col gap-1">
              {isSignedIn ? (
                NAV_LINKS.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileOpen(false)}
                    className="px-4 py-3 text-sm font-medium text-neutral-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                  >
                    {link.label}
                  </Link>
                ))
              ) : (
                <div className="pt-2 pb-4">
                  <SignInButton mode="modal" forceRedirectUrl="/dashboard">
                    <button className="w-full px-5 py-3 rounded-lg text-sm font-medium bg-white/10 border border-white/10 text-white hover:bg-white/20 transition-all duration-200">
                      Sign In
                    </button>
                  </SignInButton>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Spacer to prevent content overlap */}
      <div className="h-20" />
    </>
  );
}
