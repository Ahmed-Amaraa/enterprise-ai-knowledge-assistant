import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import {
  ApiError,
  deleteMe,
  getApiBase,
  setApiBase,
  updateMe,
  userDisplayName,
} from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export const Route = createFileRoute("/_app/account")({
  head: () => ({
    meta: [
      { title: "Account — RagDesk" },
      { name: "description", content: "Manage your RagDesk profile, theme and account settings." },
      { property: "og:title", content: "Account — RagDesk" },
      {
        property: "og:description",
        content: "Manage your RagDesk profile, theme and account settings.",
      },
    ],
  }),
  component: AccountPage,
});

function AccountPage() {
  const { user, setUser, signOut, refresh } = useAuth();
  const { theme, setTheme } = useTheme();
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [apiBase, setApiBaseValue] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirm, setConfirm] = useState("");

  useEffect(() => {
    setName(userDisplayName(user));
    setEmail(user?.email ?? "");
    setApiBaseValue(getApiBase());
  }, [user]);

  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const payload: { name?: string; email?: string; password?: string } = {
        name: name.trim(),
        email: email.trim(),
      };
      if (password) payload.password = password;
      const updated = await updateMe(payload);
      setUser(updated ?? user);
      setPassword("");
      toast.success("Account updated");
      await refresh();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Could not update your account");
    } finally {
      setBusy(false);
    }
  }

  async function removeAccount() {
    if (confirm !== "DELETE") {
      toast.error('Type DELETE to confirm.');
      return;
    }
    setBusy(true);
    try {
      await deleteMe();
      signOut();
      toast.success("Your account and data were deleted");
      void router.navigate({ to: "/login", replace: true });
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Could not delete your account");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Account</h1>
        <p className="mt-1 text-sm text-muted-foreground">Profile, appearance and danger zone.</p>
      </div>

      <section className="surface-panel p-5">
        <h2 className="font-display text-lg font-semibold">Profile</h2>
        <form onSubmit={saveProfile} className="mt-4 grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="name">Name</Label>
            <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="space-y-2 sm:col-span-2">
            <Label htmlFor="password">New password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="new-password"
              value={password}
              placeholder="Leave blank to keep your current password"
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="sm:col-span-2">
            <Button type="submit" disabled={busy}>
              {busy ? "Saving…" : "Save changes"}
            </Button>
          </div>
        </form>
      </section>

      <section className="surface-panel p-5">
        <h2 className="font-display text-lg font-semibold">Appearance</h2>
        <p className="mt-1 text-sm text-muted-foreground">Choose the theme for this account.</p>
        <div className="mt-4 flex gap-2">
          {(["light", "dark"] as const).map((option) => (
            <Button
              key={option}
              variant={theme === option ? "default" : "outline"}
              onClick={() => setTheme(option)}
              className="capitalize"
            >
              {option}
            </Button>
          ))}
        </div>
      </section>

      <section className="surface-panel p-5">
        <h2 className="font-display text-lg font-semibold">API connection</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Base URL of your FastAPI backend (auth, documents and rag endpoints).
        </p>
        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <Input
            value={apiBase}
            onChange={(e) => setApiBaseValue(e.target.value)}
            placeholder="https://api.example.com"
          />
          <Button
            variant="outline"
            onClick={() => {
              setApiBase(apiBase);
              toast.success("API base URL saved");
            }}
          >
            Save URL
          </Button>
        </div>
      </section>

      <section className="surface-panel border-destructive/40 p-5">
        <h2 className="font-display text-lg font-semibold text-destructive">Delete account</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          This permanently removes your profile, documents, embeddings and chat history.
        </p>
        <div className="mt-4 flex flex-col gap-2 sm:flex-row">
          <Input
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder="Type DELETE to confirm"
          />
          <Button variant="destructive" onClick={removeAccount} disabled={busy}>
            Delete my account
          </Button>
        </div>
      </section>
    </div>
  );
}
