import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { BrainCircuit, Plus } from "lucide-react";
import { toast } from "sonner";

import { ApiError, createConversation, fetchDocuments } from "@/lib/api";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/_app/chat/")({
  head: () => ({
    meta: [
      { title: "Chat — RagDesk" },
      { name: "description", content: "Chat with a RAG assistant grounded in your own documents." },
      { property: "og:title", content: "Chat — RagDesk" },
      {
        property: "og:description",
        content: "Chat with a RAG assistant grounded in your own documents.",
      },
    ],
  }),
  component: ChatStart,
});

function ChatStart() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const documentsQuery = useQuery({ queryKey: ["documents"], queryFn: fetchDocuments, retry: false });
  const documentCount = documentsQuery.data?.length ?? 0;

  const create = useMutation({
    mutationFn: () => createConversation("New chat"),
    onSuccess: async (conversation) => {
      await queryClient.invalidateQueries({ queryKey: ["conversations"] });
      void navigate({ to: "/chat/$conversationId", params: { conversationId: String(conversation.id) } });
    },
    onError: (error) =>
      toast.error(error instanceof ApiError ? error.message : "Could not start a new chat"),
  });

  return (
    <div className="surface-panel flex min-h-[calc(100vh-9rem)] flex-col items-center justify-center p-12 text-center bg-gradient-to-b from-card to-secondary/20 relative overflow-hidden border-border/80">
      {/* Background radial soft light */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 size-[350px] rounded-full bg-primary/5 blur-[80px] pointer-events-none" />
      
      <div className="relative flex size-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary/10 to-accent/15 border border-primary/20 shadow-sm shadow-primary/5 z-10">
        <BrainCircuit className="size-8 text-primary animate-pulse" />
      </div>
      
      <h1 className="mt-6 font-display text-3xl font-extrabold tracking-tight z-10 bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
        Start a conversation
      </h1>
      
      <p className="mt-3 max-w-md text-sm text-muted-foreground leading-relaxed font-light z-10">
        {documentCount > 0
          ? `You have ${documentCount} indexed document${documentCount === 1 ? "" : "s"} ready to query. Ask questions and receive instant grounded answers.`
          : "Upload a document first in the Documents tab so the assistant has a knowledge base to retrieve answers from."}
      </p>
      
      <Button 
        className="mt-8 rounded-xl font-bold bg-primary hover:bg-primary/95 text-primary-foreground shadow-md shadow-primary/15 hover:scale-[1.02] active:scale-95 transition-all duration-200 px-6 py-5 text-sm flex items-center gap-2 h-10.5 z-10" 
        onClick={() => create.mutate()} 
        disabled={create.isPending}
      >
        <Plus className="size-4" /> New chat
      </Button>
    </div>
  );
}
