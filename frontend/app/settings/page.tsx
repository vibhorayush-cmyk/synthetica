"use client";
import Link from "next/link";
import { AppSidebar } from "@/components/app-sidebar";
import { ProtectedPage } from "@/components/protected-page";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function SettingsPage() { return <ProtectedPage><main className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]"><AppSidebar /><section className="p-6 sm:p-10"><div className="mx-auto max-w-2xl"><header className="mb-8 flex justify-between"><div><p className="text-sm font-medium text-brand-600">Account</p><h1 className="mt-2 text-3xl font-bold">Account settings</h1></div><ThemeToggle /></header><Card><h2 className="text-lg font-semibold">Security</h2><p className="mt-2 text-sm text-slate-500">Update your password from your profile. Your datasets, templates, and history are private to your account.</p><Link href="/profile" className="mt-4 inline-flex"><Button>Open profile</Button></Link></Card></div></section></main></ProtectedPage>; }
