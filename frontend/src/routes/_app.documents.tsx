import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { CheckCircle2, FileSpreadsheet, FileText, FileType, Trash2, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";

import {
  ApiError,
  deleteDocument,
  documentName,
  fetchDocuments,
  uploadDocument,
  type DocumentItem,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const ACCEPT = ".txt,.pdf,.doc,.docx,.xls,.xlsx,.csv";

export const Route = createFileRoute("/_app/documents")({
  head: () => ({
    meta: [
      { title: "Documents — RagDesk" },
      {
        name: "description",
        content: "Upload PDF, Word, Excel or text files and manage your indexed documents.",
      },
      { property: "og:title", content: "Documents — RagDesk" },
      {
        property: "og:description",
        content: "Upload PDF, Word, Excel or text files and manage your indexed documents.",
      },
    ],
  }),
  component: DocumentsPage,
});

// Returns color-coded containers and icons for files
function fileStyles(name: string) {
  const ext = name.split(".").pop()?.toLowerCase();
  if (ext === "xls" || ext === "xlsx" || ext === "csv") {
    return {
      Icon: FileSpreadsheet,
      bg: "bg-emerald-500/10 border border-emerald-500/20",
      text: "text-emerald-600 dark:text-emerald-400"
    };
  }
  if (ext === "pdf") {
    return {
      Icon: FileType,
      bg: "bg-rose-500/10 border border-rose-500/20",
      text: "text-rose-600 dark:text-rose-400"
    };
  }
  return {
    Icon: FileText,
    bg: "bg-primary/10 border border-primary/20",
    text: "text-primary"
  };
}

function formatSize(size?: number) {
  if (!size) return null;
  const units = ["B", "KB", "MB", "GB"];
  let value = size;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(value < 10 && unit > 0 ? 1 : 0)} ${units[unit]}`;
}

function DocumentsPage() {
  const queryClient = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const documentsQuery = useQuery({ queryKey: ["documents"], queryFn: fetchDocuments, retry: false });

  const upload = useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: async (result, file) => {
      await queryClient.invalidateQueries({ queryKey: ["documents"] });
      const chunks = result?.chunks ?? result?.num_chunks;
      toast.success(`${file.name} processed`, {
        description: chunks
          ? `Text extracted, cleaned and ${chunks} embeddings stored successfully.`
          : "Text extracted, cleaned and embeddings stored successfully.",
        icon: <CheckCircle2 className="size-4" />,
      });
    },
    onError: (error, file) =>
      toast.error(`Could not process ${file.name}`, {
        description: error instanceof ApiError ? error.message : "Unexpected error",
      }),
  });

  const remove = useMutation({
    mutationFn: (id: string | number) => deleteDocument(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Document and its embeddings deleted");
    },
    onError: (error) =>
      toast.error(error instanceof ApiError ? error.message : "Could not delete the document"),
  });

  function handleFiles(files: FileList | null) {
    if (!files) return;
    Array.from(files).forEach((file) => upload.mutate(file));
  }

  const documents = documentsQuery.data ?? [];

  // Filter documents in real time based on search query
  const filteredDocuments = documents.filter((doc) => {
    const name = documentName(doc).toLowerCase();
    return name.includes(searchQuery.toLowerCase());
  });

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="font-display text-3xl font-extrabold tracking-tight">Documents</h1>
        <p className="text-sm text-muted-foreground font-light leading-relaxed">
          TXT, PDF, Word, and Excel files. Each upload is parsed, cleaned, embedded, and securely indexed for your workspace.
        </p>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        className={`surface-panel flex flex-col items-center justify-center gap-4 border-2 border-dashed p-10 text-center transition-all duration-300 bg-card/45 backdrop-blur-sm relative overflow-hidden ${
          dragging ? "border-primary bg-primary/5 scale-[1.005] shadow-lg shadow-primary/5" : "border-border hover:border-primary/40 hover:bg-card/75"
        }`}
      >
        <div className="flex size-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary/10 to-accent/15 border border-primary/20 shadow-sm shadow-primary/5">
          <UploadCloud className="size-7 text-primary" />
        </div>
        <div className="space-y-1.5">
          <p className="text-sm font-semibold tracking-tight">Drag and drop files here, or browse</p>
          <p className="text-xs text-muted-foreground font-medium">Accepts TXT, PDF, Word, Excel, or CSV files</p>
        </div>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPT}
          className="hidden"
          onChange={(e) => {
            handleFiles(e.target.files);
            e.target.value = "";
          }}
        />
        <Button 
          onClick={() => inputRef.current?.click()} 
          disabled={upload.isPending}
          className="rounded-xl font-bold bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm hover:scale-[1.02] active:scale-95 transition-all duration-200"
        >
          {upload.isPending ? "Processing upload…" : "Select files"}
        </Button>
      </div>

      {/* Library Panel */}
      <div className="surface-panel overflow-hidden bg-card/65 backdrop-blur-sm border-border/80 rounded-2xl">
        {/* Panel Header & Filter bar */}
        <div className="border-b border-border/60 px-4 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-secondary/15">
          <h2 className="font-display text-xs font-bold uppercase tracking-wider text-muted-foreground/90">
            Your library ({filteredDocuments.length})
          </h2>
          <div className="relative max-w-xs w-full">
            <Input
              type="text"
              placeholder="Search documents by name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8.5 rounded-xl text-xs bg-card focus:ring-1 focus:ring-primary/20 border-border/80"
            />
          </div>
        </div>

        {documentsQuery.isLoading ? (
          <div className="flex items-center gap-3 p-6 text-sm text-muted-foreground">
            <span className="size-2 rounded-full bg-primary animate-ping" />
            <span>Loading documents…</span>
          </div>
        ) : documentsQuery.isError ? (
          <p className="p-6 text-sm text-destructive font-medium">{(documentsQuery.error as ApiError).message}</p>
        ) : filteredDocuments.length === 0 ? (
          <p className="p-10 text-center text-sm text-muted-foreground leading-relaxed font-light">
            {searchQuery ? "No matching documents found in library." : "Nothing uploaded to your library yet."}
          </p>
        ) : (
          <ul className="divide-y divide-border/60">
            {filteredDocuments.map((doc: DocumentItem) => {
              const name = documentName(doc);
              const { Icon, bg, text } = fileStyles(name);
              const chunks = doc.chunks ?? doc.num_chunks;
              const size = formatSize(doc.size);
              const statusText = doc.status ?? "indexed";
              
              return (
                <li key={String(doc.id)} className="group flex items-center gap-4 px-4.5 py-4 transition-all duration-200 hover:bg-secondary/40">
                  <span className={`flex size-10 shrink-0 items-center justify-center rounded-xl ${bg} ${text} shadow-sm transition-transform duration-300 group-hover:scale-105`}>
                    <Icon className="size-5" />
                  </span>
                  
                  <div className="min-w-0 flex-1 space-y-1">
                    <p className="truncate text-sm font-semibold text-foreground tracking-tight">{name}</p>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="inline-flex items-center rounded-lg bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 capitalize tracking-wide">
                        {statusText}
                      </span>
                      {chunks ? (
                        <span className="inline-flex items-center rounded-lg bg-primary/10 px-2 py-0.5 text-[10px] font-bold text-primary border border-primary/20 tracking-wide">
                          {chunks} embeddings
                        </span>
                      ) : null}
                      {size ? (
                        <span className="inline-flex items-center rounded-lg bg-secondary/50 px-2 py-0.5 text-[10px] font-bold text-muted-foreground border border-border/50">
                          {size}
                        </span>
                      ) : null}
                    </div>
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Delete ${name}`}
                    onClick={() => remove.mutate(doc.id)}
                    disabled={remove.isPending}
                    className="size-9 rounded-xl hover:bg-destructive/10 text-muted-foreground/60 hover:text-destructive hover:border-destructive/20 border border-transparent transition-all duration-200 shrink-0"
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
