import { useState } from "react";
import { Navigate } from "react-router-dom";

import { ApiClientError } from "../api/client";
import { useAuth } from "../hooks/useAuth";

type LoginFieldErrors = {
  username?: string;
  password?: string;
};

export function LoginPage() {
  const { isAuthenticated, isLoading, login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<LoginFieldErrors>({});
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/links/search" replace />;
  }

  function validateFields() {
    const nextErrors: LoginFieldErrors = {};

    if (!username.trim()) {
      nextErrors.username = "Username is required.";
    }

    if (!password) {
      nextErrors.password = "Password is required.";
    }

    setFieldErrors(nextErrors);

    return Object.keys(nextErrors).length === 0;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    if (!validateFields()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await login({ username: username.trim(), password });
    } catch (error) {
      if (error instanceof ApiClientError) {
        if (error.code === "INVALID_CREDENTIALS") {
          setErrorMessage("Username or password is incorrect.");
        } else if (error.code === "VALIDATION_ERROR") {
          setErrorMessage("Please check the form fields and try again.");
        } else {
          setErrorMessage(error.message);
        }
      } else {
        setErrorMessage("Login failed.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="mx-auto max-w-md rounded-3xl border border-slate-800 bg-slate-900/90 p-6 shadow-xl shadow-slate-950/30 sm:p-7">
      <div className="space-y-2">
        <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
          Welcome back
        </span>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-100">
          Sign in to LinkDB
        </h1>
        <p className="text-sm leading-6 text-slate-400">
          Use an account created manually from the backend CLI to access the private collection.
        </p>
      </div>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-300">Username</span>
          <input
            value={username}
            onChange={(event) => {
              setUsername(event.target.value);
              setFieldErrors((current) => ({ ...current, username: undefined }));
            }}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-slate-100 outline-none transition focus:border-brand-500"
            autoComplete="username"
            required
            aria-invalid={fieldErrors.username ? "true" : "false"}
          />
          {fieldErrors.username ? (
            <span className="mt-1 block text-sm text-red-300">
              {fieldErrors.username}
            </span>
          ) : null}
        </label>

        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-slate-300">Password</span>
          <input
            type="password"
            value={password}
            onChange={(event) => {
              setPassword(event.target.value);
              setFieldErrors((current) => ({ ...current, password: undefined }));
            }}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-slate-100 outline-none transition focus:border-brand-500"
            autoComplete="current-password"
            required
            aria-invalid={fieldErrors.password ? "true" : "false"}
          />
          {fieldErrors.password ? (
            <span className="mt-1 block text-sm text-red-300">
              {fieldErrors.password}
            </span>
          ) : null}
        </label>

        {errorMessage ? (
          <p className="rounded-lg border border-red-900/70 bg-red-950/40 px-3 py-2 text-sm text-red-200">
            {errorMessage}
          </p>
        ) : null}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-xl bg-brand-500 px-4 py-2.5 font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </section>
  );
}
