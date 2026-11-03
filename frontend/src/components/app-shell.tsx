import { Link, useRouter } from "@tanstack/react-router";
import { FileText, LogOut, MessageSquare, Moon, Sun, UserCog } from "lucide-react";
import type { ReactNode } from "react";

import { userDisplayName } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { Button } from "@/components/ui/button";

const nav = [
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/account", label: "Account", icon: UserCog },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const { user, signOut } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const router = useRouter();

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-30 border-b border-border/60 bg-background/80 backdrop-blur-md transition-all duration-200">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center gap-4 px-4 sm:px-6">
          <Link to="/chat" className="flex items-center gap-2.5 group">
            <span className="relative flex size-9 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-accent font-display text-base font-extrabold text-primary-foreground shadow-md shadow-primary/10 transition-all duration-300 group-hover:scale-105 group-hover:shadow-primary/20">
              R
            </span>
            <span className="font-display text-lg font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent group-hover:text-primary transition-colors">
              RagDesk
            </span>
          </Link>

          <nav className="ml-4 flex items-center gap-1.5">
            {nav.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className="inline-flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-medium text-muted-foreground transition-all duration-200 hover:bg-secondary/60 hover:text-foreground"
                activeProps={{ className: "bg-primary/10 text-primary font-semibold shadow-[inset_0_1.5px_2px_rgba(0,0,0,0.01)]" }}
              >
                <Icon className="size-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              aria-label="Toggle theme"
              onClick={toggleTheme}
              title={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
              className="rounded-xl size-9 hover:bg-secondary/80 text-muted-foreground hover:text-foreground transition-colors"
            >
              {theme === "dark" ? <Sun className="size-4.5" /> : <Moon className="size-4.5" />}
            </Button>

            <div className="hidden items-center gap-2 rounded-full bg-secondary/60 px-3 py-1.5 text-xs font-semibold md:flex border border-border/40">
              <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-muted-foreground">{userDisplayName(user)}</span>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                signOut();
                void router.navigate({ to: "/login", replace: true });
              }}
              className="rounded-xl h-9 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30 transition-all duration-200 active:scale-95"
            >
              <LogOut className="size-4" />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto min-h-0 w-full max-w-7xl flex-1 px-4 py-6 sm:px-6">{children}</main>
    </div>
  );
}
