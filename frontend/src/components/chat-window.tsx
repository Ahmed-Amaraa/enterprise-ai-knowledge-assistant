import { useQuery, useQueryClient } from "@tanstack/react-query";
import { BrainCircuit, Check, CornerDownLeft, FileText, RefreshCw, ThumbsDown, ThumbsUp, User as UserIcon } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { ApiError, askQuestion, fetchMessages, setMessageFeedback, type ChatMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

const SUGGESTIONS = [
  "Summarize the key deliverables",
  "What are the payment and billing terms?",
  "Are there any liability clauses?",
  "What is the contract duration?"
] as const;

export function ChatWindow({ conversationId }: { conversationId: string }) {
  const queryClient = useQueryClient();
  const [input, setInput] = useState("");
  const [pending, setPending] = useState<ChatMessage[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const messagesViewportRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const messagesQuery = useQuery({
    queryKey: ["messages", conversationId],
    queryFn: () => fetchMessages(conversationId),
    retry: false,
  });

  const messages = [...(messagesQuery.data ?? []), ...pending];

  useEffect(() => {
    const viewport = messagesViewportRef.current;
    if (viewport) {
      viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" });
    }
  }, [messages.length]);

  useEffect(() => {
    textareaRef.current?.focus();
    setPending([]);
  }, [conversationId]);

  async function submit(textOverride?: string, isRegeneration = false) {
    const question = (textOverride ?? input).trim();
    if (!question || isAsking) return;
    if (!isRegeneration) {
      setPending((prev) => [...prev, { id: `u-${Date.now()}`, role: "user", content: question }]);
    }
    setInput("");
    setIsAsking(true);

    try {
      const data = await askQuestion(conversationId, question);
      const answer = data.answer ?? data.content ?? data.message ?? "";
      setPending((prev) => [
        ...prev,
        {
          id: data.message_id ?? `a-${Date.now()}`,
          role: "assistant",
          content: answer || "I could not find an answer in your documents.",
          ...(data.sources ? { sources: data.sources } : {}),
        },
      ]);
      await queryClient.invalidateQueries({ queryKey: ["conversations"] });
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "The assistant could not answer");
    } finally {
      setIsAsking(false);
      textareaRef.current?.focus();
    }
  }

  return (
    <div className="flex h-[calc(100vh-9rem)] flex-col surface-panel overflow-hidden bg-card/45 backdrop-blur-sm border-border/80 rounded-2xl">
      {/* Messages Viewport */}
      <div ref={messagesViewportRef} className="min-h-0 flex-1 space-y-6 overflow-y-auto p-5 scrollbar-thin">
        {messagesQuery.isLoading ? (
          <div className="flex items-center gap-3 text-sm text-muted-foreground p-3">
            <span className="size-2 rounded-full bg-primary animate-ping" />
            <span>Loading conversation history…</span>
          </div>
        ) : messages.length === 0 ? (
          <div className="mx-auto max-w-xl py-12 text-center relative">
            <div className="mx-auto flex size-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary/10 to-accent/15 border border-primary/20 shadow-sm shadow-primary/5">
              <BrainCircuit className="size-7 text-primary" />
            </div>
            <h2 className="mt-5 font-display text-2xl font-extrabold tracking-tight">Ask your documents</h2>
            <p className="mt-2 max-w-sm mx-auto text-sm text-muted-foreground leading-relaxed font-light">
              Every answer is grounded in the files you uploaded. Click a suggestion below or type your query to start.
            </p>
            
            {/* Quick Action Suggestion Cards */}
            <div className="mt-8 grid gap-3 sm:grid-cols-2 text-left">
              {SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => {
                    setInput(suggestion);
                    textareaRef.current?.focus();
                  }}
                  className="p-4 rounded-xl border border-border/60 bg-card hover:border-primary/30 hover:bg-secondary/40 text-sm font-medium text-foreground transition-all duration-200 shadow-[0_1.5px_3px_rgba(0,0,0,0.01)] hover:shadow-md hover:shadow-primary/5 hover:-translate-y-0.5 cursor-pointer"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageBubble
              key={message.id}
              message={message}
              previousQuestion={messages[index - 1]?.role === "user" ? messages[index - 1].content : ""}
              onRegenerate={(question) => void submit(question, true)}
            />
          ))
        )}

        {isAsking && (
          <div className="flex items-center gap-3 text-sm text-muted-foreground p-2 rounded-xl bg-secondary/20 w-fit animate-pulse border border-border/30">
            <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <BrainCircuit className="size-4 text-primary" />
            </span>
            <span className="font-semibold tracking-wide text-xs">Searching library and generating answer…</span>
          </div>
        )}
      </div>

      {/* Input Form Area */}
      <div className="border-t border-border/50 bg-secondary/15 p-4">
        <div className="relative flex items-end gap-2 p-1.5 rounded-2xl border border-border bg-card shadow-sm focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/10 transition-all duration-250">
          <Textarea
            ref={textareaRef}
            value={input}
            rows={1}
            placeholder="Ask something about your documents…"
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            className="flex-1 max-h-32 min-h-[2.5rem] py-2 px-3 resize-none bg-transparent border-0 focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground/60 text-sm focus:outline-none"
          />
          <Button 
            onClick={() => submit()} 
            disabled={isAsking || !input.trim()} 
            size="icon" 
            aria-label="Send"
            className="size-9 rounded-xl bg-primary hover:bg-primary/95 text-primary-foreground hover:scale-[1.02] active:scale-95 shadow-sm transition-all flex items-center justify-center shrink-0 disabled:opacity-40 disabled:hover:scale-100 disabled:pointer-events-none cursor-pointer"
          >
            <CornerDownLeft className="size-4" />
          </Button>
        </div>
        <p className="mt-2 text-[10px] text-muted-foreground/80 font-medium px-1">Enter to send · Shift + Enter for a new line</p>
      </div>
    </div>
  );
}

function MessageBubble({
  message,
  previousQuestion,
  onRegenerate,
}: {
  message: ChatMessage;
  previousQuestion: string;
  onRegenerate: (question: string) => void;
}) {
  const isUser = message.role === "user";
  const content = message.content;

  return (
    <div className={`flex gap-3.5 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-xl bg-primary/10 border border-primary/20 text-primary shadow-sm">
          <BrainCircuit className="size-4.5" />
        </span>
      )}
      <div className={`max-w-[72ch] space-y-2.5 ${isUser ? "text-right" : "text-left"}`}>
        <div
          className={
            isUser
              ? "inline-block rounded-2xl rounded-tr-xs bg-gradient-to-tr from-primary to-primary/95 px-4.5 py-3 text-sm text-primary-foreground shadow-md shadow-primary/5 leading-relaxed font-medium text-left"
              : "inline-block max-w-[78ch] rounded-2xl rounded-tl-xs bg-card/85 border border-primary/10 px-5 py-4 text-sm text-foreground shadow-[0_8px_24px_-18px_rgba(0,0,0,0.28)] leading-7 font-normal whitespace-pre-wrap break-words"
          }
        >
          <ReactMarkdown
            components={{
              h1: ({ children }) => <h3 className="mb-2 mt-1 font-display text-base font-bold text-foreground">{children}</h3>,
              h2: ({ children }) => <h3 className="mb-2 mt-1 font-display text-base font-bold text-foreground">{children}</h3>,
              h3: ({ children }) => <h3 className="mb-2 mt-1 font-display text-sm font-bold text-foreground">{children}</h3>,
              p: ({ children }) => <p className="my-2 first:mt-0 last:mb-0">{children}</p>,
              ul: ({ children }) => <ul className="my-2 list-disc space-y-1 pl-5">{children}</ul>,
              ol: ({ children }) => <ol className="my-2 list-decimal space-y-1 pl-5">{children}</ol>,
              a: ({ children, href }) => <a className="font-semibold text-primary underline underline-offset-2" href={href}>{children}</a>,
              strong: ({ children }) => <strong className="font-bold text-foreground">{children}</strong>,
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
        
        {message.sources && message.sources.length > 0 && (
          <div className="flex flex-col gap-1.5 text-left pt-1.5 px-0.5">
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/90">Sources Cited</span>
            <ul className="flex flex-wrap gap-1.5">
              {message.sources.map((source, index) => (
                <li
                  key={`${source}-${index}`}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border/60 bg-secondary/50 px-2.5 py-1.5 text-xs font-semibold text-muted-foreground hover:bg-secondary hover:text-foreground transition-all duration-200 shadow-[0_1px_2px_rgba(0,0,0,0.015)] cursor-default"
                >
                  <FileText className="size-3.5 text-muted-foreground/80" />
                  {source}
                </li>
              ))}
            </ul>
          </div>
        )}
        {!isUser && message.id && !message.id.startsWith("a-") && (
          <MessageFeedback
            message={message}
            question={previousQuestion}
            onRegenerate={() => onRegenerate(previousQuestion)}
          />
        )}
      </div>
      {isUser && (
        <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-xl bg-accent/15 border border-accent/20 text-accent font-semibold shadow-sm">
          <UserIcon className="size-4.5" />
        </span>
      )}
    </div>
  );
}

function MessageFeedback({
  message,
  question,
  onRegenerate,
}: {
  message: ChatMessage;
  question: string;
  onRegenerate: () => void;
}) {
  const [saving, setSaving] = useState(false);
  const [selectedFeedback, setSelectedFeedback] = useState(message.feedback);

  async function vote(feedback: "useful" | "not_useful") {
    setSaving(true);
    try {
      await setMessageFeedback(message.id, feedback);
      setSelectedFeedback(feedback);
    } catch {
      toast.error("Could not save your feedback");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex items-center gap-1 text-muted-foreground">
      <button disabled={saving} onClick={() => void vote("useful")} aria-label="Useful answer" className={`rounded-lg p-1.5 transition-colors hover:bg-secondary hover:text-emerald-600 ${message.feedback === "useful" ? "text-emerald-600" : ""}`}>
        {selectedFeedback === "useful" ? <Check className="size-3.5" /> : <ThumbsUp className="size-3.5" />}
      </button>
      <button disabled={saving} onClick={() => void vote("not_useful")} aria-label="Not useful answer" className={`rounded-lg p-1.5 transition-colors hover:bg-secondary hover:text-destructive ${message.feedback === "not_useful" ? "text-destructive" : ""}`}>
        <ThumbsDown className={`size-3.5 ${selectedFeedback === "not_useful" ? "fill-current" : ""}`} />
      </button>
      {selectedFeedback === "not_useful" && (
        <button onClick={onRegenerate} disabled={saving} className="ml-1 inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-semibold text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground">
          <RefreshCw className="size-3" /> Regenerate
        </button>
      )}
      {question && <span className="sr-only">Question: {question}</span>}
    </div>
  );
}
