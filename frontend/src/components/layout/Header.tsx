import { Link } from "react-router-dom";
import { useState } from "react";

import { useAuth } from "../../hooks/useAuth";

export function Header() {
  const { isAuthenticated, logout, user } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  async function handleLogout() {
    setIsLoggingOut(true);

    try {
      await logout();
    } finally {
      setIsLoggingOut(false);
    }
  }

  return (
    <header className="sticky top-0 z-20 border-b border-slate-800/90 bg-slate-950/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <div className="min-w-0">
          <Link to="/links/search" className="text-lg font-semibold tracking-tight text-slate-100">
            LinkDB
          </Link>
          <p className="mt-1 text-sm text-slate-400">
            Private collection of links shared with friends.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
          {isAuthenticated && user ? (
            <>
              <nav className="flex flex-wrap items-center gap-2">
                <Link
                  to="/links/search"
                  className="rounded-lg border border-slate-700 px-3 py-2 text-slate-100 transition hover:bg-slate-800"
                >
                  Search
                </Link>
                <Link
                  to="/links/new"
                  className="rounded-lg border border-slate-700 px-3 py-2 text-slate-100 transition hover:bg-slate-800"
                >
                  New Link
                </Link>
                <Link
                  to="/links/read-later"
                  className="rounded-lg border border-slate-700 px-3 py-2 text-slate-100 transition hover:bg-slate-800"
                >
                  Read Later
                </Link>
              </nav>
              <span className="rounded-full border border-slate-800 bg-slate-900 px-3 py-1.5 text-slate-200">
                Signed in as {user.username}
              </span>
              <button
                type="button"
                onClick={() => void handleLogout()}
                disabled={isLoggingOut}
                className="rounded-lg border border-slate-700 px-3.5 py-2 text-slate-100 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isLoggingOut ? "Logging out..." : "Logout"}
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="rounded-lg border border-slate-700 px-3.5 py-2 text-slate-100 transition hover:bg-slate-800"
            >
              Login
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
