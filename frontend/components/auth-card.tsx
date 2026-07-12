"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { BrandLockup } from "@/components/brand/brand-lockup";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";

export function LoginCard() {
  const { login } = useAuth(); const router = useRouter(); const params = useSearchParams();
  const [error, setError] = useState<string | null>(null); const [pending, setPending] = useState(false);
  async function submit(data: FormData) { setPending(true); setError(null); try { await login(String(data.get("email")), String(data.get("password"))); router.replace(params.get("next") || "/workspace"); } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to sign in."); } finally { setPending(false); } }
  return <AuthShell title="Welcome back" description="Sign in to generate and manage your datasets."><form action={submit} className="space-y-4"><Input name="email" label="Email" type="email" required /><Input name="password" label="Password" type="password" required />{error && <ErrorMessage message={error} />}<Button className="w-full" disabled={pending}>{pending ? "Signing in…" : "Sign in"}</Button><div className="flex justify-between text-sm"><Link className="text-brand-600" href="/forgot-password">Forgot password?</Link><Link className="text-brand-600" href="/register">Create account</Link></div></form></AuthShell>;
}

export function RegisterCard() {
  const { register } = useAuth(); const router = useRouter(); const [error, setError] = useState<string | null>(null); const [pending, setPending] = useState(false);
  async function submit(data: FormData) { setPending(true); setError(null); try { await register(String(data.get("fullName")), String(data.get("email")), String(data.get("password"))); router.replace("/workspace"); } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to create your account."); } finally { setPending(false); } }
  return <AuthShell title="Create your account" description="Start generating private, analytics-ready datasets."><form action={submit} className="space-y-4"><Input name="fullName" label="Full name" required /><Input name="email" label="Email" type="email" required /><Input name="password" label="Password" type="password" hint="12+ characters with uppercase, lowercase, and a number." required />{error && <ErrorMessage message={error} />}<Button className="w-full" disabled={pending}>{pending ? "Creating account…" : "Create account"}</Button><p className="text-center text-sm text-slate-500">Already have an account? <Link className="text-brand-600" href="/login">Sign in</Link></p></form></AuthShell>;
}

export function ForgotPasswordCard() {
  const [message, setMessage] = useState<string | null>(null); const [error, setError] = useState<string | null>(null);
  async function submit(data: FormData) { setError(null); try { const response = await (await import("@/services/auth-service")).requestPasswordReset(String(data.get("email"))); setMessage(`${response.message}${response.reset_token ? " In this mock environment, your reset token has been generated." : ""}`); } catch (cause) { setError(cause instanceof Error ? cause.message : "Unable to start password reset."); } }
  return <AuthShell title="Reset your password" description="We’ll create a mocked reset token for your account."><form action={submit} className="space-y-4"><Input name="email" label="Email" type="email" required />{error && <ErrorMessage message={error} />}{message && <p className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700">{message}</p>}<Button className="w-full">Request reset token</Button><p className="text-center text-sm"><Link className="text-brand-600" href="/login">Back to login</Link></p></form></AuthShell>;
}

function AuthShell({ title, description, children }: { title: string; description: string; children: React.ReactNode }) { return <main className="grid min-h-screen place-items-center bg-slate-50 p-5 dark:bg-slate-950"><section className="w-full max-w-md rounded-3xl bg-white p-7 shadow-xl dark:bg-slate-900"><Link href="/" className="mb-8 block"><BrandLockup /></Link><h1 className="text-2xl font-bold">{title}</h1><p className="mt-2 text-sm text-slate-500">{description}</p><div className="mt-7">{children}</div></section></main>; }
function Input({ label, hint, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string; hint?: string }) { return <label className="block text-sm font-medium"><span>{label}</span><input className="input mt-1.5" {...props} />{hint && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}</label>; }
function ErrorMessage({ message }: { message: string }) { return <p role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{message}</p>; }
