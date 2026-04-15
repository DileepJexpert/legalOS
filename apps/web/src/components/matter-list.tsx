"use client";

import Link from "next/link";
import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import type { MatterSummary } from "@legalos/contracts";
import { Badge, Button, Card, Field, Input } from "@legalos/ui";
import { clearAuthToken } from "@/lib/auth";
import { createBrowserApiClient } from "@/lib/api/client";

const STAGES = [
  { value: "pre_filing", label: "Pre-filing" },
  { value: "filing", label: "Filing" },
  { value: "notice", label: "Notice" },
  { value: "evidence", label: "Evidence" },
  { value: "arguments", label: "Arguments" },
  { value: "orders", label: "Orders" }
] as const;

function formatDate(value: string | null) {
  if (!value) return "Not scheduled";
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium" }).format(new Date(value));
}

interface NewMatterForm {
  title: string;
  reference_code: string;
  forum: string;
  stage: string;
  next_hearing_date: string;
  summary: string;
}

const EMPTY_FORM: NewMatterForm = {
  title: "",
  reference_code: "",
  forum: "",
  stage: "pre_filing",
  next_hearing_date: "",
  summary: ""
};

export function MatterList() {
  const [matters, setMatters] = useState<MatterSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewMatterForm>(EMPTY_FORM);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  function loadMatters() {
    const api = createBrowserApiClient();
    void api.getMatters().then((result) => {
      if (result.ok) {
        setMatters(result.data);
      } else {
        setError(result.message);
      }
    });
  }

  useEffect(() => {
    loadMatters();
  }, []);

  function handleField(field: keyof NewMatterForm) {
    return (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
    };
  }

  async function handleCreate(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setCreating(true);
    setCreateError(null);
    try {
      const api = createBrowserApiClient();
      await api.createMatter({
        title: form.title,
        reference_code: form.reference_code,
        forum: form.forum,
        stage: form.stage as "pre_filing" | "filing" | "notice" | "evidence" | "arguments" | "orders",
        next_hearing_date: form.next_hearing_date || null,
        summary: form.summary || null
      });
      setForm(EMPTY_FORM);
      setShowForm(false);
      loadMatters();
    } catch (cause) {
      setCreateError(cause instanceof Error ? cause.message : "Failed to create matter");
    } finally {
      setCreating(false);
    }
  }

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-4 border-b border-white/10 pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-2">
          <div className="text-xs uppercase tracking-[0.24em] text-slate-400">Matter index</div>
          <h1 className="text-3xl font-semibold text-white">Available matter workspaces</h1>
          <p className="max-w-3xl text-sm leading-6 text-slate-300">
            Open a matter cockpit, continue the upload workflow, or move into verified research.
          </p>
        </div>
        <div className="flex gap-3">
          <Button onClick={() => setShowForm((v) => !v)}>
            {showForm ? "Cancel" : "+ New Matter"}
          </Button>
          <Button
            variant="ghost"
            onClick={() => {
              clearAuthToken();
              window.location.href = "/login";
            }}
          >
            Sign out
          </Button>
        </div>
      </header>

      {/* New matter form */}
      {showForm && (
        <Card className="border-white/10 bg-white/5 p-6 backdrop-blur">
          <div className="mb-4 text-lg font-medium text-white">Create new matter</div>
          <form className="grid gap-4 sm:grid-cols-2" onSubmit={handleCreate}>
            <Field label="Case title *">
              <Input
                value={form.title}
                onChange={handleField("title")}
                placeholder="e.g. Ramesh Kumar v. State of UP"
                required
              />
            </Field>

            <Field label="Reference code *">
              <Input
                value={form.reference_code}
                onChange={handleField("reference_code")}
                placeholder="e.g. UP-HC-2026-001"
                required
              />
            </Field>

            <Field label="Forum / Court *">
              <Input
                value={form.forum}
                onChange={handleField("forum")}
                placeholder="e.g. Allahabad High Court"
                required
              />
            </Field>

            <Field label="Stage">
              <select
                value={form.stage}
                onChange={handleField("stage")}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
              >
                {STAGES.map((s) => (
                  <option key={s.value} value={s.value} className="bg-slate-900">
                    {s.label}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Next hearing date">
              <Input
                type="date"
                value={form.next_hearing_date}
                onChange={handleField("next_hearing_date")}
              />
            </Field>

            <Field label="Brief summary">
              <Input
                value={form.summary}
                onChange={handleField("summary")}
                placeholder="One-line description of the matter"
              />
            </Field>

            {createError && (
              <div className="col-span-2 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-100">
                {createError}
              </div>
            )}

            <div className="col-span-2 flex justify-end gap-3">
              <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={creating}>
                {creating ? "Creating…" : "Create matter"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {error && (
        <Card>
          <div className="text-sm text-red-100">{error}</div>
        </Card>
      )}

      <div className="grid gap-4">
        {matters.map((matter) => (
          <Card key={matter.id} className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="space-y-2">
              <div className="text-lg font-medium text-white">{matter.title}</div>
              <div className="text-sm text-slate-300">
                {matter.reference_code} • {matter.forum}
              </div>
              <div className="text-sm text-slate-400">{matter.summary ?? "No summary recorded yet."}</div>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Badge variant="success">{matter.status}</Badge>
              <Badge variant="neutral">{matter.document_count} docs</Badge>
              <Badge variant="warning">Next: {formatDate(matter.next_hearing_date)}</Badge>
              <Button asChild>
                <Link href={`/matters/${matter.id}`}>Open matter</Link>
              </Button>
            </div>
          </Card>
        ))}

        {!matters.length && !error && (
          <Card>
            <div className="text-sm text-slate-300">Loading matters…</div>
          </Card>
        )}
      </div>
    </section>
  );
}
