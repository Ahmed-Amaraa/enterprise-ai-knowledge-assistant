import { createFileRoute, Link, useRouter } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { ApiError, loginRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in — RagDesk" },
      { name: "description", content: "Sign in to RagDesk to chat with your own documents." },
      { property: "og:title", content: "Sign in — RagDesk" },
      { property: "og:description", content: "Sign in to RagDesk to chat with your own documents." },
    ],
  }),
  component: LoginPage,
});

function LoginPage() {
  const { setSession, isAuthenticated } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (isAuthenticated) void router.navigate({ to: "/chat", replace: true });
  }, [isAuthenticated, router]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const { token, user } = await loginRequest(email.trim(), password);
      await setSession(token, user);
      toast.success("Welcome back");
      void router.navigate({ to: "/chat", replace: true });
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Sign in failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to keep chatting with your knowledge base."
      footer={
        <>
          Don't have an account?{" "}
          <Link to="/signup" className="font-medium text-primary hover:underline">
            Create one
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />
        </div>
        <Button type="submit" className="w-full" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </Button>
      </form>
    </AuthLayout>
  );
}

export function AuthLayout({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_1fr] bg-background">
      {/* Left panel - Decorative Branding */}
      <div className="relative hidden flex-col justify-between overflow-hidden bg-[#0d0a1b] p-12 text-primary-foreground lg:flex">
        {/* Glow Spheres */}
        <div className="absolute top-1/4 -left-1/4 size-[400px] rounded-full bg-primary/15 blur-[100px] pointer-events-none animate-pulse" style={{ animationDuration: '6s' }} />
        <div className="absolute bottom-1/4 -right-1/4 size-[450px] rounded-full bg-accent/15 blur-[120px] pointer-events-none animate-pulse" style={{ animationDuration: '8s' }} />
        
        {/* Top Header */}
        <div className="flex items-center gap-3 z-10">
          <span className="relative flex size-10 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-accent font-display text-lg font-black text-white shadow-lg shadow-primary/20">
            R
          </span>
          <span className="font-display text-xl font-bold tracking-tight text-white">
            RagDesk
          </span>
        </div>

        {/* Dynamic Center Branding Content */}
        <div className="relative my-auto max-w-md space-y-7 z-10 text-left">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-md text-xs font-semibold text-accent/90 tracking-wide uppercase">
              ✨ Grounded AI Assistant
            </div>
            <h1 className="font-display text-4xl font-extrabold leading-tight tracking-tight text-white lg:text-5xl">
              Your documents, <span className="bg-gradient-to-r from-accent to-purple-300 bg-clip-text text-transparent">finally answerable.</span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              Upload PDFs, Word files, spreadsheets, or plain text. We extract, clean, embed, and index them, allowing you to retrieve accurate answers from your own knowledge base.
            </p>
          </div>

          {/* Abstract Glassmorphic Feature card */}
          <div className="relative p-6 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-md shadow-xl overflow-hidden group hover:border-white/15 transition-all duration-300">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-accent/5 opacity-40 pointer-events-none" />
            <div className="flex gap-4 items-start relative z-10">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-accent to-purple-500 text-white font-bold shadow-md shadow-accent/15">
                AI
              </div>
              <div className="space-y-1 text-left">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">No Hallucinations</h4>
                <h3 className="text-sm font-semibold text-white">Instant Citations & References</h3>
                <p className="text-xs text-slate-300 leading-relaxed font-light">Every response generated is backed by source snippets from your verified corporate library, so you can audit the results instantly.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Footer metadata */}
        <div className="flex items-center justify-between text-xs text-slate-400 z-10 border-t border-white/5 pt-4">
          <span>Secure Enterprise Workspace</span>
          <span className="flex items-center gap-1.5 font-medium text-emerald-400">
            <span className="size-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            Strictly Private
          </span>
        </div>
      </div>

      {/* Right panel - Form Content */}
      <div className="flex items-center justify-center px-6 py-16 bg-gradient-to-b from-background to-secondary/20">
        <div className="w-full max-w-sm space-y-8">
          <div className="space-y-2.5 text-center sm:text-left">
            <h2 className="font-display text-3xl font-extrabold tracking-tight text-foreground">{title}</h2>
            <p className="text-sm text-muted-foreground">{subtitle}</p>
          </div>
          <div className="p-6 sm:p-8 rounded-2xl border border-border/50 bg-card shadow-lg shadow-foreground/5 backdrop-blur-sm transition-all duration-300">
            {children}
          </div>
          <p className="text-center text-sm text-muted-foreground font-medium">{footer}</p>
        </div>
      </div>
    </div>
  );
}
